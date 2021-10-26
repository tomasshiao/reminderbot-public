import logging
import telegram
import os, sys
import random
import datetime, pytz
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import timezone, timedelta

import messages as msg

# Logging config
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# ENV 
TOKEN = os.getenv("TOKEN")
mode = os.getenv("MODE")
REMINDER_CHAT = int(os.getenv("REMINDER_CHAT"))
GIF = str(os.getenv("GIF_ID"))
ME = str(os.getenv("HEROKU_APP_NAME"))

# Set Timezone UTC-03:00
diferencia = timedelta(hours=-3)
zona_horaria = timezone(diferencia)

# Set Constants
def setConstants():
    finde = datetime.datetime.now().today().astimezone(zona_horaria).weekday() > 4
    hoy = datetime.datetime.now().today().astimezone(zona_horaria).strftime("%d/%m/%Y")
    feriado = hoy in msg.feriados_2021
    return (finde, hoy, feriado)

# Aux Func
def me_llaman(message):
    hayOtroBot = False
    if message.chat.type == 'private':
        return True
    msj = message.text.split()
    command = msj.pop(0)
    if '@' in command:
        hayOtroBot = True
    if not hayOtroBot:
        return True
    at_me = '@' + ME
    logger.info(f"{at_me}")
    if at_me in command:
        return True
    return False

def remove_punctuation(msj):
    no_punc = ""
    for char in msj:
        if char not in msg.punctuations:
            no_punc = no_punc + char
    return no_punc

def random_estoy_de_paro():
    return msg.numero%msg.divisor == 0

def feedback_message_selector():
    g = random.randint(0, 319)
    lunes = datetime.datetime.now().today().astimezone(zona_horaria).weekday() == 0
    viernes = datetime.datetime.now().today().astimezone(zona_horaria).weekday() == 4
    mmj = not (setConstants()[0] or lunes or viernes)
    condicion = (g%2 == 0 and not mmj)
    if condicion:
        if setConstants()[0]:
            f = random.randint(0, len(msg.finde_feedbacks)- 1)
            return msg.finde_feedbacks[f]
        if lunes:
            l = random.randint(0, len(msg.lunes_feedbacks)- 1)
            return msg.lunes_feedbacks[l]
        if viernes:
            v = random.randint(0, len(msg.viernes_feedbacks) - 1)
            return msg.viernes_feedbacks[v]
    else:
        x = random.randint(0, len(msg.mmj_feedbacks) - 1)
        return msg.mmj_feedbacks[x]

def truchada_parche(message):
    message = str(message)
    return True if (msg.parche in message) else False

# Easter Egg Evals
def saludos(msj):
    msj = msj.lower()
    msj = remove_punctuation(msj)
    saludar = False
    x = 0
    while x < len(msg.saludos_mas_de_una_palabra) and not saludar:
        if msg.saludos_mas_de_una_palabra[x] in msj:
            saludar = True
        x += 1
    if saludar:
        return True
    msj = msj.split()
    y = 0
    while y < len(msg.saludos) and not saludar:
        if msg.saludos[y] in msj:
            saludar = True
        y += 1
    return saludar

def easter_egg1(msj):
    sendEasterEgg = False
    msj = msj.lower()
    if msg.ee1 in msj:
        sendEasterEgg = True
    msj = msj.lower().split()
    for m in msj:
        if m in msg.apuestas:
            sendEasterEgg = True
    return sendEasterEgg

def easter_egg2(msj):
    sendEasterEgg = False
    msj = msj.lower()
    if msg.ee2 in msj:
        sendEasterEgg = True
    return sendEasterEgg

# Easter Egg Functions
def contesto_mensaje(update, context):
    logger.info(f"Le contesto a: USER = {update.effective_user['username']} (ID = {update.effective_user['id']})")
    p = random.randint(0, len(msg.posibles_rtas) - 1)
    context.bot.send_message(chat_id=update.message.chat.id, parse_mode="HTML", text=f"{msg.posibles_rtas[p]}")

def aceptar_apuesta(message, context):
    k = random.randint(0, len(msg.aceptar_apuesta_mensajes) - 1)
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.aceptar_apuesta_mensajes[k]}")

def ee2(message, context):
    k = random.randint(0, len(msg.ee2_response) - 1)
    if k == len(msg.ee2_response) - 1:
        context.bot.send_message(chat_id=message.chat.id, parse_mode="Markdown", text=msg.ee2_particular_response)
        return
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.ee2_response[k]}")

def saludo(message, context):
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.slds_paro)
        return
    s = random.randint(0, len(msg.saludos_rta) - 1)
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.saludos_rta[s]}")

def ee3(message, context):
    w = random.randint(0, len(msg.ee3_response) - 1)
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.ee3_response[w]}")

def ee4(message, context):
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee4_paro)
        return
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee4_rta)

def ee5(message, context):
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee5_paro)
        return
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee5_rta)

def ee6(message, context):
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee6_paro)
        return
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee6_rta)

def ee7(message, context):
    if setConstants()[0]:
        t = random.randint(0, len(msg.ee7_finde_response) - 1)
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.ee7_finde_response[t]}")
    elif setConstants()2]:
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ee7_feriado_response)
    else:
        s = random.randint(0, len(msg.ee7_response) - 1)
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.ee7_response[s]}")

# Functions
def start(update, context):
    message = update.message
    print(update)
    logger.info(f"USER = {update.effective_user['username']} pressed start.")
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        update.message.reply_text(msg.dia_del_bot)
        return
    random_condition = (random.randint(0, 123984) % 29 == 0)
    if random_condition:
        name = update.effective_user['first_name']
        update.message.reply_text(f"Hola {name}")
        return
    i = random.randint(0, len(msg.welcomeMessages)-2) if (not setConstants()[0]) else random.randint(0, len(msg.welcomeMessages)-1)
    update.message.reply_text(f"{msg.welcomeMessages[i]}")

def help(update, context):
    message = update.message
    logger.info(f"USER = {update.effective_user['username']} pressed help.")
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.caida_del_bot)
        return
    j = random.randint(0, len(msg.helpMessages) - 3) if (not setConstants()[0]) else random.randint(0, len(msg.helpMessages) - 1)
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.helpMessages[j]}")

def at_cry(update, context):
    message = update.message
    name = update.effective_user['first_name']
    logger.info(f"USER = {update.effective_user['username']} pressed cry.")
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        name = 'che' if name is None else name
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.estoy_garca.format(name))
        return
    if truchada_parche(message):
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.lloron)
    else:
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.lloron)

def at_ok(update, context):
    message = update.message
    name = update.effective_user['first_name']
    logger.info(f"USER = {update.effective_user['username']} pressed ok.")
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        name = '??' if name is None else name
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.bot_deprimido.format(name))
        return
    context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.ok)

def search(update, context):
    message = update.message
    logger.info(f"USER = {update.effective_user['username']} wants to search for something.")
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.no_busco_nada)
        return
    msj = message.text.split()
    if len(msj) == 1:
        context.bot.send_message(chat_id=message.chat.id, parse_mode="Markdown", text=msg.input_erroneo)
    else:
        comando = msj.pop(0)
        text = message.text[len(comando)+1:]
        # qwant con %20, resto con +
        s = random.randint(0, len(msg.searchers) -1)
        if s != 3:
            busqueda = text.replace(' ', '+')
        else:
            busqueda = text.replace(' ', '%20')
        link = msg.searchers[s].format(busqueda)
        context.bot.send_message(chat_id=message.chat.id, parse_mode="Markdown", text=f"[Here you go!]({link})")

def at_sq(update, context):
    message = update.message
    logger.info(f"USER = {update.effective_user['username']} asked for a stupid question.")
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=msg.dejame_descansar)
        return
    s = random.randint(0, len(msg.sqs) - 1)
    context.bot.send_message(chat_id=message.chat.id, parse_mode="Markdown", text=f"{msg.sqs[s]}")

def easterEggs(update, context):
    logger.info(f"USER = {update.effective_user['username']} sent a message I've read.")
    text = remove_punctuation(update.message.text)
    message = update.message
    if update.message.chat.type == "private":
        if saludos(text):
            logger.info(f"USER = {update.effective_user['username']} sent a salutation.")
            saludo(message, context)
        else:
            logger.info(f"USER = {update.effective_user['username']} sent a private chat.")
            contesto_mensaje(update, context)
    else:
        if easter_egg1(text):
            logger.info(f"USER = {update.effective_user['username']} challenged me (or maybe not but I'm taking my chances).")
            aceptar_apuesta(message, context)
        elif easter_egg2(text):
            logger.info(f"USER = {update.effective_user['username']}.")
            ee2(message, context)
        elif msg.ee3 in text.lower().split():
            logger.info(f"USER = {update.effective_user['username']} typed {msg.ee3}.")
            ee3(message, context)
        elif msg.ee4 in text.lower().split():
            logger.info(f"USER = {update.effective_user['username']} typed {msg.ee4}.")
            ee4(message, context)
        elif msg.ee5 in text.lower().split():
            logger.info(f"USER = {update.effective_user['username']} typed {msg.ee5}.")
            ee5(message, context)
        elif msg.ee6 in text.lower().split() or msg.ee6b in text.lower().split():
            logger.info(f"USER = {update.effective_user['username']} typed {msg.ee6}.")
            ee6(message, context)
        elif msg.ee7 in text.lower().split():
            logger.info(f"USER = {update.effective_user['username']} forgot {msg.ee7}.")
            ee7(message, context)

def feedback(update, context):
    message = update.message
    if not me_llaman(message):
        return
    if random_estoy_de_paro():
        context.bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f"{msg.no_me_importa_tu_feedback}")
        return
    msj = message.text.split()
    if len(msj) == 1:
        context.bot.send_message(chat_id=update.message.chat.id, parse_mode="HTML", text=msg.input_nulo)
    else:
        context.bot.send_message(chat_id=update.message.chat.id, parse_mode="HTML", text=feedback_message_selector())

# Recordatorios
def reminder1(context):
    if not setConstants()[0] and not setConstants()[2]:
        d = random.randint(0, len(msg.r1_texts) - 1)
        context.bot.send_message(chat_id=context.job.context, parse_mode="HTML", text=f"{msg.r1_texts[d]}")
    else:
        if setConstants()[0] and setConstants()[2]:
            logger.info(msg.finde_y_feriado)
        elif setConstants()[0]:
            logger.info(msg.hoy_es_finde)
        else:
            logger.info(msg.hoy_es_feriado)

def reminder2(context):
    if not setConstants()[0] and not setConstants()[2]:
        context.bot.send_message(chat_id=context.job.context, parse_mode="HTML", text=msg.text_to_send)
        context.bot.send_animation(chat_id=context.job.context, animation=GIF)
    else:
        if setConstants()[0] and setConstants()[2]:
            logger.info(msg.finde_y_feriado)
        elif setConstants()[0]:
            logger.info(msg.hoy_es_finde)
        else:
            logger.info(msg.hoy_es_feriado)

# Jobs
def statusChecker(context: telegram.ext.CallbackContext):
    finde = setConstants()[0]
    hoy = setConstants()[1]
    feriado = setConstants()[2]
    logger.info(f"FINDE => {finde}; HOY=> {hoy}; FERIADO => {feriado}")
    logger.info("Fecha y hora loggueo: " + str(datetime.datetime.now().today().astimezone(zona_horaria)))
    div = msg.checkerDiv
    logger.info(f"Divisor => {div}")
    if msg.checkerNum % div == 0:
        logger.info(f"{msg.basura}\n")

if mode == "dev": 
    # Desarrollo
    def run(updater):
        updater.start_polling()
        print("bot cargado")
        updater.idle()
elif mode == "prod":
    # Desplegado
    def run(updater):
        '''
        # Para webhook y dyno web.
        PORT = int(os.environ.get('PORT', '8443'))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url="https://"+ HEROKU_APP_NAME +".herokuapp.com/" + TOKEN)
        '''
        # Para dyno worker y que no se desactive después de 30 min.
        updater.start_polling()
        updater.idle()
        logger.info('Bot started.')
else:
    logger.info("No mode set.")
    sys.exit()

if __name__ == "__main__":
    # Bot INFO
    bot = telegram.Bot(token = TOKEN)

# Enlace
updater = Updater(bot.token, use_context=True)

# Dispatcher
dp = updater.dispatcher

# Job Queue
jq = updater.job_queue
jq.run_repeating(statusChecker, interval=msg.interval, first=msg.first, name="checker")
jq.run_daily(reminder1, datetime.time(hour=9, minute=30, tzinfo=pytz.timezone('America/Argentina/Buenos_Aires')), days=(0, 1, 2, 3, 4), context=REMINDER_CHAT, name="r1")
jq.run_daily(reminder2, datetime.time(hour=17, minute=30, tzinfo=pytz.timezone('America/Argentina/Buenos_Aires')), days=(0, 1, 2, 3, 4), context=REMINDER_CHAT, name="r2")

# Handlers
# CommandHandler(command, function)
dp.add_handler(CommandHandler("start", start, pass_job_queue=True))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("cry", at_cry))
dp.add_handler(CommandHandler("ok", at_ok))
dp.add_handler(CommandHandler("search", search))
dp.add_handler(CommandHandler("stupid_question", at_sq))
dp.add_handler(CommandHandler("feedback", feedback))
dp.add_handler(MessageHandler(Filters.text, easterEggs))

run(updater)
