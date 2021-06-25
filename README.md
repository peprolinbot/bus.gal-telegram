# bus.gal-telegram

<img src="logo.svg" alt="bus.gal-telegram" width=200/>

[![@busGal_bot](https://img.shields.io/badge/Stable%20bot-@busGal_bot-blue?logo=telegram&style=plastic)](https://telegram.me/busGal_bot)
![GitHub](https://img.shields.io/github/license/peprolinbot/bus.gal-telegram)

Telegram Bot that serves you info about the buses from the Galician Public Transport Network.

_Bot de Telegram que te informa de los horarios de los buses de la red de transporte público de galicia._

Data is obtained through  [bus.gal-api.](https://github.com/peprolinbot/bus.gal-api)

_Los datos se obtienen a través de [bus.gal-api](https://github.com/peprolinbot/bus.gal-api)_

## Hosting your own

If you want to host your own instance of the bot, it is as easy as a docker container.

_Si quieres hostear tu propia instancia del bot es tan sencillo como un contenedor de docker_

### With Docker

So the command is:

_Así que el comando es el siguiente:_
 
```bash
docker run -d --name bus.gal-telegram -v $PWD/config:/etc/busgal-telegram \
    -e BUS.GAL_BOT_NAME="bus.gal" \
    -e BUS.GAL_TELEGRAM_TOKEN="YourToken" \
    ghcr.io/peprolinbot/bus.gal-telegram
```

#### Environment Variables

| Name                     | Description |
|--------------------------|-------------|
| `BUS.GAL_BOT_NAME`       | The name the bot will use to present itself. _El nombre que el bot usará para presentarse a si mismo_
| `BUS.GAL_TELEGRAM_TOKEN` | The Telegram bot token obtained from @BotFather. _El bot token de Telegram que obtuviste de @BotFather_
| `BUS.GAL_DATABASE_PATH`  | Absolute path to the database file. The directory must exist. (optional, defaults to `/etc/bus.gal-telegram/database.db`). _Ruta absoluta al archivo de base de datos. El directorio padre debe existir. (opcional, por defecto es `/etc/bus.gal-telegram/database.db`)_

## Disclaimer

This project is not endorsed by, directly affiliated with, maintained by, sponsored by or in any way officially related with la Xunta de Galicia, the bus operators or any of the companies involved in the [bus.gal](https://www.bus.gal/) website and the [app](https://play.google.com/store/apps/details?id=gal.xunta.transportepublico).

_Este proyecto no cuenta con soporte de, no está afiliado con, mantenido por, patrocinado por ni de cualquier otra manera oficialmente conectado con la Xunta de Galicia, los operadores de autobuses o cualquiera de las empresas involucradas en la página web [bus.gal](https://www.bus.gal/) y su respectiva [aplicación](https://play.google.com/store/apps/details?id=gal.xunta.transportepublico)._

## Credits
- Logo: https://pixabay.com/images/id-2027077/
