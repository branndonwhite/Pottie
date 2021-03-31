from flask import Flask, request, abort
import json
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *
import requests

app = Flask(__name__)

access_key = json.load(open('accessKey.json'))

line_bot_api = LineBotApi(access_key['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(access_key['CHANNEL_SECRET'])
trefle_token = access_key['TREFLE_TOKEN']

commandList = "Here is how you interact with me. It all starts with '~'.\n~help: A guide to help you understand more what I can do for now\n~command: reminds you of all available commands\n~search: get plants with any keyword you type\n~common: get plants with their common name\n~species: get plants with their species name\n~neat facts: show you some neat facts about plants\n~bye: say goodbye to me in a group or chat room"

def createCarouselQuery(url):
    response = requests.get(url)
    obj = response.json()
    carouselList = []

    if(len(obj['data']) != 0):
        for data in obj['data']:
            if(data['image_url'] != None and data['common_name'] != None):
                carousel = CarouselColumn(
                    thumbnail_image_url= data['image_url'],
                    title= data['common_name'],
                    text= data['scientific_name'],
                    actions= [
                        URIAction(
                            label= 'More Detail',
                            uri= "https://en.wikipedia.org/wiki/"+data['scientific_name'].replace(' ', '_')
                        )
                    ]
                )
                carouselList.append(carousel)
            
    if(len(carouselList) == 0):
        message = TextSendMessage(text="Sorry I can't find any plant with this name.")
    else:
        message = TemplateSendMessage(
            alt_text= 'Here is what I find',
            template= CarouselTemplate(
                columns= carouselList
            )
        )
    
    return message

def createSpeciesDetail(url):
    response = requests.get(url)
    obj = response.json()

    # if the API gets the data
    if('data' in obj.keys()): 
        data = obj['data']
        # set common name to scientific name if common name is null
        if(data['common_name'] == None):
            data['common_name'] = data['scientific_name']
        if(data['family_common_name'] == None):
            data['family_common_name'] = '-'

        bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url=data['image_url'],
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover'
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # Common name
                        TextComponent(text=data['common_name'], wrap=True, size='xl', weight='bold'),
                        # Scientific name
                        TextComponent(text=data['scientific_name'], wrap=True, size='md', style='italic'),
                        # genus and family name
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='vertical',
                                    spacing='sm',
                                    margin='md',
                                    contents=[
                                        TextComponent(
                                            text="Genus",
                                            color='#1d96a3',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text=data['genus'],
                                            wrap=True,
                                            size='sm',
                                            flex=5,
                                        ),
                                    ]
                                ),
                                BoxComponent(
                                    layout='vertical',
                                    spacing='sm',
                                    margin='md',
                                    contents=[
                                        TextComponent(
                                            text="Family",
                                            color='#1d96a3',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text=data['family'],
                                            wrap=True,
                                            size='sm',
                                            flex=5,
                                        ),
                                    ]
                                ),
                                BoxComponent(
                                    layout='vertical',
                                    spacing='sm',
                                    margin='md',
                                    contents=[
                                        TextComponent(
                                            text="Family Common Name",
                                            color='#1d96a3',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text=data['family_common_name'],    
                                            wrap=True,
                                            size='sm',
                                            flex=5,
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout='vertical',
                    contents=[
                        # websiteAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(
                                label='More Detail', 
                                uri="https://en.wikipedia.org/wiki/"+data['scientific_name'].replace(' ', '_')
                            )
                        )
                    ]
                )
            )
        message = FlexSendMessage(alt_text="Here is what I get", contents=bubble)
    else:
        message = TextSendMessage(text="Sorry I can't find it. Maybe you can specify it.")

    return message

def createFactCarousel(data_list):
    carouselList = []
    
    for query in data_list:
        carousel = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "image",
                    "url": query['image_url'],
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "1:1",
                    "gravity": "center"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "position": "absolute",
                    "background": {
                    "type": "linearGradient",
                    "angle": "0deg",
                    "endColor": "#00000000",
                    "startColor": "#00000099"
                    },
                    "width": "100%",
                    "height": "40%",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": query['title'],
                            "size": "xl",
                            "color": "#ffffff",
                            "wrap": True
                        }
                        ],
                        "spacing": "xs"
                    }
                    ],
                    "position": "absolute",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                    "paddingAll": "20px"
                }
                ],
                "paddingAll": "0px",
                "action": {
                    "type": "message",
                    "label": query['text'],
                    "text": "~fact " + query['text']
                }
            }
        }

        carouselList.append(carousel)

    content = {
        'type': 'carousel',
        'contents': carouselList
    }

    message = FlexSendMessage(
        alt_text= 'Neat Facts!',
        contents= content
    )

    return message

def createFactDetail(img_url, common_name, description, scientific_name):
    buttons_template = ButtonsTemplate(
        thumbnail_image_url=img_url,
        image_aspect_ratio='square',
        title=common_name, 
        text=description, 
        actions=[
            URIAction(
                label='Further Reading', 
                uri='https://en.wikipedia.org/wiki/'+scientific_name
            )
        ]
    )

    message = TemplateSendMessage(
        alt_text='Fact Detail', 
        template=buttons_template
    )

    return message

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
        
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    # send greeting to user who added this bot
    greeting = "I can help you finding any plant you want to know more :)\n\n"
    message = TextSendMessage(text= greeting + commandList)

    line_bot_api.reply_message(event.reply_token, message)

@handler.add(JoinEvent)
def handle_join(event):
    # send greeting to the group or multichat
    greeting = "Hello everyone! Thank you for inviting me to this " + event.source.type + ".\n\nI can help you finding any plant you want to know more :)\n\n"
    message = TextSendMessage(text= greeting + commandList)

    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MemberJoinedEvent)
def handle_memberJoin(event):
    # send greeting to new member joined in group or multichat
    greeting = "Hello new member! I can help you find the plant you wanted.\nType '~help' to see available command."
    message = TextSendMessage(text= greeting)

    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    text = event.message.text
    message = None

    if text == '~help':
        reply_item = [
            QuickReplyButton(
                action=MessageAction(label="Command list", text="~command")
            ),
            QuickReplyButton(
                action=MessageAction(label="Neat facts!", text="~neat facts")
            ),
            QuickReplyButton(
                action=MessageAction(label="Common name?", text="~ask common")
            ),
            QuickReplyButton(
                action=MessageAction(label="Scientific name?", text="~ask scientific")
            ),
            QuickReplyButton(
                action=MessageAction(label="Searching plant", text="~all search")
            )
        ]

        message = TextSendMessage(
            text="Here is some action to help you understand more about each search or do a command faster ^_^",
            quick_reply=QuickReply(items=reply_item)
        )

    elif text == '~command':
        # show all available command list
        message = TextSendMessage(text=commandList)

    elif '~search' in text:
        # get info by any keyword
        name = text[8:]

        if(len(name)) == 0:
            message = TextSendMessage(text="Seems like you haven't type any keyword. Type '~search <keyword>' to get a result.")
        else:
            url = "https://trefle.io/api/v1/plants/search?token="+ trefle_token + "&q=" + name + "&limit=10"
            message = createCarouselQuery(url)

    elif '~common' in text:
        # get info by common name
        name = text[8: ]

        if(len(name) == 0):
            message = TextSendMessage(text="Seems like you haven't type a common name. Type '~common <common name>' to get a result.")
        else:
            url = "https://trefle.io/api/v1/plants?token="+ trefle_token + "&filter[common_name]=" + name + "&limit=10"
            message = createCarouselQuery(url)

    elif '~species' in text:
        # get info by species name
        name = text[9:]

        if(len(name) == 0):
            message = TextSendMessage(text="Seems like you haven't type a species name. Type '~species <species name>' to get a result.")
        else:
            name = name.replace(' ', '-')
            url = "https://trefle.io/api/v1/species/" + name.lower() + "?token="+ trefle_token
            message = createSpeciesDetail(url)

    elif text == '~neat facts':
        # show some neat facts in carousel
        data_list = [
            {
                'image_url': "https://calscape.com/ExtData/allimages/900/Sequoia_sempervirens_900_4.jpg",
                'title': "Meet The Tallest Tree In The World!",
                'text': "tallest tree"
            },
            {
                'image_url': "https://cdn.britannica.com/s:1500x700,q:85/48/12548-004-68A15563/Cucumber.jpg",
                'title': "Is this fruit or veggie?",
                'text': "fruit/veggie"
            },
            {
                'image_url': "https://upload.wikimedia.org/wikipedia/commons/9/98/Pachira_aquatica_Tree.jpg",
                'title': "This plant bring you a luck?",
                'text': "lucky tree"
            },
            {
                'image_url': "https://upload.wikimedia.org/wikipedia/commons/1/12/Bl%C3%BCten_der_Dictamnus_albus.jpg",
                'title': "Don't let their beauty fool you",
                'text': "flammable plant"
            },
            {
                'image_url': "https://www.carnivorousplants.org/sites/default/files/images/GrowingGuides/Dionaea6a.jpg",
                'title': "Will it bite you or not?",
                'text': "chomp chomp"
            },
            {
                'image_url': "https://buffalo-niagaragardening.com/wp-content/uploads/2015/10/Morty-corpse-flower-in-leaf-by-Stofko1.jpg",
                'title': "Guess what is this?",
                'text': "this stalk"
            }
        ]

        message = createFactCarousel(data_list)

    elif text == '~fact tallest tree':
        img_url = "https://www.anticcolonial.com/wp-content/naturelovers/uploads/2016/04/01.jpg"
        description = "Named Hyperion, it is reaching up to 115.5 m in height"
        message = createFactDetail(img_url, "Coast Redwood", description, "Sequoia_sempervirens")

    elif text == '~fact fruit/veggie':
        img_url = "https://upload.wikimedia.org/wikipedia/commons/9/96/ARS_cucumber.jpg"
        description = "Yes, it's a fruit as it grows from flowers & contains seeds"
        message = createFactDetail(img_url, "Cucumber", description, "Cucumis_sativus")

    elif text == '~fact lucky tree':
        img_url = "https://upload.wikimedia.org/wikipedia/commons/8/8f/Money_Tree.jpg"
        description = "In East Asia, it's associated with good financial fortune"
        message = createFactDetail(img_url, "Guiana Chestnut", description, "Pachira_aquatica")

    elif text == '~fact flammable plant':
        img_url = "https://4.bp.blogspot.com/-KfHXYMkiLLs/VvK24RqCLLI/AAAAAAAABGY/4tAUVyCM9yMdiQ6j8TR09ANVjElKMZBrg/s1600/Diptam-Pflanzen-Dictamnus-albus-1631.jpg"
        description = "It produces volatile oils that can catch fire in hot weather"
        message = createFactDetail(img_url, "Burning Bush", description, "Dictamnus_albus")

    elif text == '~fact chomp chomp':
        img_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/Dionaea%2C_muscoid_fly.jpg"
        description = "No, it only catches its prey—chiefly insects and arachnids"
        message = createFactDetail(img_url, "Venus Flytrap", description, "Dionaea_muscipula")

    elif text == '~fact this stalk':
        img_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/COLLECTIE_TROPENMUSEUM_Indonesische_mannen_poseren_bij_twee_verschillende_soorten_Amorphophallus_planten_waaronder_een_in_bloei_staande_Amorphophallus_Titanum_TMnr_60042790.jpg"
        description = "This is Titan arum tree-like leaf when it doesn't flower"
        message = createFactDetail(img_url, "Corpse Flower", description, "Amorphophallus_titanum")

    elif text == '~ask common':
        text = "The common name on a plant is the name that most people know in some region. You need to know the common name from the region to region may vary. \n\nTry to type '~common tangerine' or '~common moon orchid' to get the result :D"
        message = TextSendMessage(text=text)

    elif text == '~ask scientific':
        text = "The scientific name is a formal system of naming species of living things by giving each a name composed of two parts, both of which use Latin grammatical forms, although they can be based on words from other languages.\nThe first part of the name – the generic name – identifies the genus to which the species belongs, while the second part – the specific name or specific epithet – identifies the species within the genus.\n\nTry to type '~scientific Rosa pendulina' to get the result :D"
        message = TextSendMessage(text=text)

    elif text == '~all search':
        text = "There are 3 types of searching currently available.\n\nSearch: search plants with any keyword including color name\nSearch by common name: search plant with a common name you type\nSearch species: search a plant with its scientific name"
        message = TextSendMessage(text=text)

    elif text == '~bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text='See you again in future!')
            )
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text='See you again in future!')
            )
            line_bot_api.leave_room(event.source.room_id)
        else:
            message = TextSendMessage(text="I'm afraid you will be alone here...")
    
    elif text[0] == '~':
        # notify if user type incorrect command
        message = TextSendMessage(text="Seems like you type the wrong keyword. Type '~command' for the command list.")
    
    if message != None:
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
