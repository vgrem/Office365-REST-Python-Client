# How to connect to SharePoint Online with certificate credentials  

### Create a self-signed certificate

####  Register certificate

For demonstration purposes we will create a self signed certificate via Azure Cloud Shell:
- Open Cloud Shell
- Enter the following code into Cloud Shell to create a self signed certificate:
  `openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout privateKey.key -out selfsigncert.crt`
- Export the certificate by running the following command in Cloud Shell:
  `cat selfsigncert.crt privateKey.key > selfsigncert.pem`
  
  
#### Register your certificate with Azure AD

You can associate the certificate-based credential with the client application in Azure AD from the Azure portal. To associate the credential, follow [official docs](https://docs.microsoft.com/en-us/azure/cosmos-db/certificate-based-authentication#register-your-certificate-with-azure-ad) steps


#### Grant permissions

You'll need to add additional permissions in order to use SharePoint API. 
Choose Add a permission and under Microsoft APIs, select `SharePoint`, and then select `Application permissions`, for instance :


- `SharePoint`
  - `Application permissions`
    - `Sites`
      - `Sites.FullControl.All`





### API 

`ClientContext.connect_with_certificate(site_url, client_id,thumbprint, certificate_path)`

where 

```
site_url - SharePoint site url
client_id - The OAuth client id of the calling application. 
thumbprint - hex encoded thumbprint of the certificate
certificate_path - path to a PEM encoded certificate private key
```

### Usage


```
app_settings = {
    'url': 'https://contoso.sharepoint.com/',  
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f', 
    'thumbprint': "6B36FBFC86FB1C019EB6496494B9195E6D179DDB",
    'certificate_path': 'cert.pem'
}

ctx = ClientContext.connect_with_certificate(app_settings['url'],
                                             app_settings['client_id'],
                                             app_settings['thumbprint'],
                                             app_settings['certificate_path'])

current_web = ctx.web
ctx.load(current_web)
ctx.execute_query()
print("{0}".format(current_web.url))
```




### References

 - [How To Create a Self Signed Certificate in Azure using Cloud Shell](https://techcommunity.microsoft.com/t5/itops-talk-blog/how-to-create-a-self-signed-certificate-in-azure-using-cloud/ba-p/401403)
 - [Create a self-signed certificate via PowerShell](https://docs.microsoft.com/en-us/powershell/module/pkiclient/new-selfsignedcertificate?view=win10-ps)   
