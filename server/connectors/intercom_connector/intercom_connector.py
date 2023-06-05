import requests
import os
import json
from typing import Dict, List, Optional
from models.models import AppConfig, Document, ConnectorId, DocumentConnector, AuthorizationResult
from appstatestore.statestore import StateStore
import base64


class IntercomConnector(DocumentConnector):
    connector_id: ConnectorId = ConnectorId.intercom
    config: AppConfig
    headers: Dict = {}

    def __init__(self, config: AppConfig):
        super().__init__(config=config)

    async def authorize_api_key(self) -> AuthorizationResult:
        pass

    async def authorize(self, account_id: str, auth_code: Optional[str], metadata: Optional[Dict]) -> AuthorizationResult:
        connector_credentials = StateStore().get_connector_credential(self.connector_id, self.config)
        try: 
            client_id = connector_credentials['client_id']
            client_secret = connector_credentials['client_secret']
            authorization_url = f"https://app.intercom.com/oauth?client_id={client_id}"
            redirect_uri = "https://link.psychic.dev/oauth/redirect"
        except Exception as e:
            raise Exception("Connector is not enabled")
        
        if not auth_code:
            return AuthorizationResult(authorized=False, auth_url=authorization_url)

        try:
            # encode in base 64
            headers = {
                "Content-Type": "application/json", 
            }

            data = {
                'code': auth_code,
                'client_id': client_id,
                'client_secret': client_secret,
            }

            response = requests.post(f"https://api.intercom.io/auth/eagle/token", headers=headers, json=data)

            creds = response.json()

            creds_string = json.dumps(creds)

            access_token = creds['access_token']

            headers['Authorization'] = f"Bearer {access_token}"

            response = requests.get("https://api.intercom.io/me", headers=headers)

            app_info = response.json()
            print(app_info)

            workspace_name = app_info['app']['name']
            

            
            
        except Exception as e:
            print(e)
            raise Exception("Unable to get access token with code")

        
        new_connection = StateStore().add_connection(
            config=self.config,
            credential=creds_string,
            connector_id=self.connector_id,
            account_id=account_id,
            metadata={
                'workspace_name': workspace_name,
            }
        )
        return AuthorizationResult(authorized=True, connection=new_connection)


    async def load(self, account_id: str) -> List[Document]:
        connection = StateStore().load_credentials(self.config, self.connector_id, account_id)
        credential_string = connection.credential
        credential_json = json.loads(credential_string)

        documents: List[Document] = [{
            'title': 'Test',
            'content': 'This is an example help article. You can edit it by clicking the edit button in the top right corner. You can also add new articles by clicking the "Add Article" button in the top left corner.',
            'uri': 'https://www.intercom.com/Help-Article-Example-1d1b1b1b1b1b4c4c4c4c4c4c4c4c4c4c',
        }]

        return documents





            

    
