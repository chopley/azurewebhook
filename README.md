# Python Flask app on Azure App Service Web

This is the start of a framework that can be used to deploy API service endpoints onto Azure Webapps using python Flask


For more information, please see the [Python on App Service Quickstart docs](https://docs.microsoft.com/en-us/azure/app-service-web/app-service-web-get-started-python).

git clone https://github.com/chopley/azurewebhook.git

cd azurewebhook

pip3 install -r requirements.txt

python3 main.py

This should have the process running locally.

Now we need to deploy it onto Azure. Firstly create an Azure login.

az webapp deployment user set --user-name <username> --password <password>
az group create --name myResourceGroup --location "West Europe"
az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku FREE
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name <app_name> --runtime "python|3.4" --deployment-local-git
git remote add azure <deploymentLocalGitUrl-from-create-step>
git push azure master
http://<app_name>.azurewebsites.net

Now it should be working.

You can test it by:
curl -i -H "Content-Type: application/json" -X POST -d "@addData.json" http://transferto.azurewebsites.net/getProducts

You will need a json definition file that looks like:
```javascript
{
        "apikey":"", #from transferto
        "apisecret": "", #from transferto
        "phone" : "", #the phone number that will be uploaded to
        "token": "", #from transferto
        "url_login" : "", #from transferto
        "login" : "", #from transferto
        "airtime_url" : "", #from transferto
        "products_url" : "", #from transferto
        "products_val" : "", #a string (e.g. 30MB) that will be matched against available products to decide which product ID to load
        "simulate" : "0" #whether (1) or not (0) to simulate the transaction 
}
```
# Contributing

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
