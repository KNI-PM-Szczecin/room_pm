pipeline {
    agent any
    options {
        skipDefaultCheckout()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }
    triggers { pollSCM('H/2 * * * *') }
    environment {
        PATH = "/Applications/Docker.app/Contents/Resources/bin:/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
        DOCKER_HOST = 'unix:///Users/wiit1/.docker/run/docker.sock'
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker-ci"
        COMPOSE_PROJECT_NAME = 'room_pm'
        ROOMPM_CONFIG_PATH = '/Users/wiit1/Containers/room_pm/config.json'
        ROOMPM_DATA_PATH = '/Users/wiit1/Containers/room_pm/data'
    }
    stages {
        stage('Pobranie kodu') {
            steps { git branch: 'main', url: 'https://github.com/KNI-PM-Szczecin/room_pm.git' }
        }
        stage('Konfiguracja') {
            steps {
                sh 'mkdir -p "$DOCKER_CONFIG"'
                writeFile file: '.docker-ci/config.json', text: '{"cliPluginsExtraDirs":["/Applications/Docker.app/Contents/Resources/cli-plugins"]}'
                sh '''
                    set -eu
                    docker info >/dev/null
                    test -s "$ROOMPM_CONFIG_PATH" || {
                        echo "Brak konfiguracji: $ROOMPM_CONFIG_PATH"
                        exit 1
                    }
                    mkdir -p "$ROOMPM_DATA_PATH"
                    chmod 600 "$ROOMPM_CONFIG_PATH"
                '''
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    env.ROOMPM_IMAGE = "room-pm:${env.GIT_COMMIT}-${env.BUILD_NUMBER}"
                }
            }
        }
        stage('Budowa obrazu') {
            steps {
                writeFile file: 'docker-compose.deploy.yml', text: '''services:
  room-pm:
    image: ${ROOMPM_IMAGE:-room-pm:latest}
    build: .
    container_name: room_pm_bot
    restart: unless-stopped
    environment:
      PYTHONUNBUFFERED: "1"
      TZ: Europe/Warsaw
    volumes:
      - type: bind
        source: ${ROOMPM_CONFIG_PATH:-./config.json}
        target: /roompm/config.json
        read_only: true
        bind:
          create_host_path: false
      - ${ROOMPM_DATA_PATH:-./data}:/data
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
'''
                sh '''
                    set -eu
                    printf '\nconfig.json\n.docker-ci/\n' >> .dockerignore
                    docker compose -f docker-compose.deploy.yml build --pull room-pm
                '''
            }
        }
        stage('Sprawdzenie konfiguracji i Supabase') {
            steps {
                sh '''
                    set -eu
                    docker run --rm -i --entrypoint python \
                        --mount "type=bind,source=$ROOMPM_CONFIG_PATH,target=/roompm/config.json,readonly" \
                        "$ROOMPM_IMAGE" - <<'PY'
import asyncio
import tempfile
import nextcord
from nextcord.ext import commands
from utilities.baseUtils import ConfigReader
from utilities.dcDatabase import DB
from cogs.room import RoomCog
from cogs.events import EventsCog
from cogs.messages_forward import MessagesForwardCog
async def check_menu():
    view = RoomCog.HourSelectView()
    menu = view.to_components()[0]['components'][0]
    assert menu.get('custom_id'), 'Menu godzin nie ma custom_id'
    assert len(menu['options']) == 14
    view.stop()
asyncio.run(check_menu())
config = ConfigReader('config.json')
assert config.get_bot_token(), 'Brak tokenu Discord'
assert config.get_supabase_url().startswith('https://'), 'Brak URL Supabase'
assert config.get_supabase_key(), 'Brak klucza Supabase'
client = commands.Bot(intents=nextcord.Intents.default())
room = RoomCog(client, config)
with tempfile.TemporaryDirectory() as directory:
    database = DB(directory, 'check.db')
    for cog in (room, EventsCog(client, config, database), MessagesForwardCog(client, config, database)):
        client.add_cog(cog)
# Sprawdź obie relacje używane przez wyszukiwanie sal, bez zapisu do bazy.
try:
    room.roomFinder.db.table('rooms').select('name, building!inner(name)').limit(1).execute()
    room.roomFinder.db.table('roomschedule').select('*').limit(1).execute()
except Exception:
    raise SystemExit('Nie udało się odczytać rooms/roomschedule z Supabase; sprawdź konfigurację i uprawnienia') from None
print('Konfiguracja, wszystkie moduły i odczyt Supabase: OK')
PY
                '''
            }
        }
        stage('Wdrożenie') {
            steps { sh 'docker compose -f docker-compose.deploy.yml up -d --no-build room-pm' }
        }
        stage('Połączenie z Discordem') {
            steps {
                sh '''
                    set -eu
                    for attempt in $(seq 1 45); do
                        state=$(docker inspect --format '{{.State.Status}} {{.RestartCount}}' room_pm_bot)
                        test "$state" = 'running 0' || {
                            docker logs --tail 80 room_pm_bot
                            echo "Bot nie pracuje stabilnie: $state"
                            exit 1
                        }
                        if docker logs room_pm_bot 2>&1 | grep -q '>>> Client is ready.'; then
                            docker logs --tail 40 room_pm_bot
                            echo 'RoomPM połączony z Discordem.'
                            exit 0
                        fi
                        sleep 2
                    done
                    docker logs --tail 80 room_pm_bot
                    echo 'Brak potwierdzenia gotowości Discord w ciągu 90 sekund.'
                    exit 1
                '''
            }
        }
    }
}
