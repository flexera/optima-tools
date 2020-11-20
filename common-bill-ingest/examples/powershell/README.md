

## Authentication

```sh

$RefreshToken = 'retrieve from user settings in console'

   $contentType = "application/json"
   $oAuthHeader = @{"X_API_VERSION" = "1.5" }
   $oAuthBody = @{
       "grant_type"    = "refresh_token";
       "refresh_token" = $RefreshToken
   } | ConvertTo-Json
   Write-Verbose "Retrieving access token..."
   $oAuthResult = Invoke-RestMethod -Uri "https://us-3.rightscale.com/api/oauth2" -Method Post -Headers $oAuthHeader -ContentType $contentType -Body $oAuthBody
   $accessToken = $oAuthResult.access_token

    $UserHeader = @{"Authorization" = "Bearer $accessToken"}

```




## Create a bill upload job
```sh

 $billUploadCreateBody = @{
    "billConnectId" = "cbi-ci-private-123456";
    "billingPeriod" = "2019-09";
  } | ConvertTo-Json



$billUploadCreate = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads" -Method POST -Headers $UserHeader -ContentType $contentType  -Body $billUploadCreateBody
```
## Post data to upload job

```sh
$fileToUpload = 'billing-data-vmware-2019-09.csv'
$fileContentsBody = Get-Content $fileName| Out-String

$billUploadPost = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads/$billUploadID/files/$fileName" -Method POST -Headers $UserHeader -ContentType $contentType  -Body $fileContentsBody


```
## Commit the upload job
```sh
    $billUploadCommitBody = @{
      "operation" = "commit";
    } | ConvertTo-Json

    $billUploadCommit = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads/$billUploadID/operations" -Method POST -Headers $UserHeader -ContentType $contentType  -Body $billUploadCommitBody
```

## List Upload Jobs
```sh
  $billUploadList = Invoke-RestMethod -Uri "https://optima.rightscale.com/optima/orgs/$OrganizationId/billUploads" -Method GET -Headers $UserHeader -ContentType $contentType  
  

```