   $fileName = "PrivateFSBillings_test.csv"
   $RefreshToken = "dddddddddddddddd"
   $contentType = "application/json"
   $OrganizationId="222222224"
   $billUploadID =  "318ba336-eaff-4f7f-9636-c60640ddfe50"
   

   $contentType = "application/json"
   $oAuthHeader = @{"X_API_VERSION" = "1.5" }
   $oAuthBody = @{
       "grant_type"    = "refresh_token";
       "refresh_token" = $RefreshToken
   } | ConvertTo-Json
   Write-Verbose "Retrieving access token..."
   $oAuthResult = Invoke-RestMethod -Uri "https://us-3.rightscale.com/api/oauth2" -Method Post -Headers $oAuthHeader -ContentType $contentType -Body $oAuthBody
   $accessToken = $oAuthResult.access_token

 



    $fileContentAsString = Get-Content $fileName| Out-String

    $fileBody = @{
        "data" = $fileContentAsString;
    } | ConvertTo-Json

 
 
   $getUserHeader = @{
    "Authorization" = "Bearer $accessToken"
   }

   $billUploadCreate = @{
    "billConnectId" = "cbi-ci-private-1314441533";
    "billingPeriod" = "2020-09";
  } | ConvertTo-Json
  $billUploadCreate
    $fileUploadResp= "";

#List BillUploads
    $billUploadList = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads" -Method GET -Headers $getUserHeader -ContentType $contentType  
    $billUploadList

#Create Bill Upload Job
    # $billUploadCreate = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads" -Method POST -Headers $getUserHeader -ContentType $contentType  -Body $billUploadCreate

    # $billUploadCreate

    
 #Post the files to the Bill Upload Job
    # $fileUploadResp = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads/$billUploadID/files/$fileName" -Method POST -Headers $getUserHeader -ContentType $contentType  -Body $fileContentAsString

    # $fileUploadResp


    $billUploadCommit = @{
      "operation" = "commit";
    } | ConvertTo-Json


#Commit/Finalize the files to the Bill Upload Job for processing.
    # $fileUploadCommit = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads/$billUploadID/operations" -Method POST -Headers $getUserHeader -ContentType $contentType  -Body $billUploadCommit

    # $fileUploadCommit


 
 