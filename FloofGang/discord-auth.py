#!/usr/bin/env python3
# Copyright of Lizzy Trickster (Lizzy Green)

from social_core.backends.oauth import BaseOAuth2


class DiscordOAuth2(BaseOAuth2):
    """Discord OAuth2 authentication Backend"""

    # def auth_html(self):
    #     pass # FIXME Work out what this is for?

    name = "discord"
    AUTHORIZATION_URL = 'https://discord.com/api/oauth2/authorize'
    ACCESS_TOKEN_URL = 'https://discord.com/api/oauth2/token'
    REVOKE_TOKEN_URL = "https://discord.com/api/oauth2/token/revoke"
    ACCESS_TOKEN_METHOD = "POST"
    REFRESH_TOKEN_METHOD = "POST"
    REDIRECT_STATE = False
    DEFAULT_SCOPE = ['identify']
    SCOPE_SEPARATOR = ' '
    EXTRA_DATA = [
        ('username', 'username'),
        ('discriminator', 'discriminator'),
        ('id', 'discord_id'),
        ('verified', 'verified')
    ]

    def get_user_details(self, response):
        return {
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': '',
            'last_name': ''

        }

    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(
            'https://discord.com/api/users/@me',
            headers={'Authorization': f"Bearer {access_token}", "Client-ID": self.setting('KEY')}
        )
