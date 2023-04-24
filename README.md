Steps to Run

1. Generate google account credentials at https://console.cloud.google.com/apis/dashboard and add given redirect_uris while generating
2. Save it in project with name credentials.json which will look like this
{
  "web":
      {
         "client_id":"xxx",
         "project_id":"xxx",
         "auth_uri":"xxx",
         "token_uri":"xxx",
         "auth_provider_x509_cert_url":"xxx",
         "client_secret":"xxx",
         "redirect_uris":["https://google-calendar-integration.preetbhatia.repl.co/rest/v1/calendar/redirect/"]
      }
}

3. After saving credentials.json we can run server