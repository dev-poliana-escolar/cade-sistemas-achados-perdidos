from social_core.backends.oauth import BaseOAuth2
from apps.items.models import Item


class SuapOAuth2(BaseOAuth2):
    name = 'suap'
    AUTHORIZATION_URL = 'https://suap.ifrn.edu.br/o/authorize/'
    ACCESS_TOKEN_URL = 'https://suap.ifrn.edu.br/o/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    ID_KEY = 'identificacao'
    RESPONSE_TYPE = 'code'
    REDIRECT_STATE = True
    STATE_PARAMETER = True
    DEFAULT_SCOPE = ['identificacao', 'email', 'documentos_pessoais']

    def user_data(self, access_token, *args, **kwargs):
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.get_json(
            'https://suap.ifrn.edu.br/api/rh/eu/',
            headers=headers,
        )
        extra = self.get_json(
            'https://suap.ifrn.edu.br/api/rh/meus-dados/',
            headers=headers,
        )
        response['curso'] = extra.get('vinculo', {}).get('curso', '')
        return response

    def get_user_details(self, response):
        nome = response.get('nome_social') or response.get('nome_registro', '')
        partes = nome.split()
        return {
            'username': response.get('identificacao', ''),
            'email': response.get('email_secundario', ''),
            'first_name': partes[0] if partes else '',
            'last_name': partes[-1] if len(partes) > 1 else '',
        }

    def get_user_id(self, details, response):
        return response.get('identificacao')