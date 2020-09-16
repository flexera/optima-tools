<#
.SYNOPSIS
Sets Flexera Optima Bill Adjustments.
.DESCRIPTION
This will set a Bill Adjustment based on a provided json file containing the Bill Adjustment rules.
.PARAMETER OrganizationId
The Flexera CMP Organization Id.
.PARAMETER Endpoint
The Cloud Management endpoint your refresh token was generated against. Valid values: us-3.rightscale.com, us-4.rightscale.com
.PARAMETER RefreshToken
The users refresh token
.PARAMETER BillAdjustmentJSON
The path to JSON file containing the Bill Adjustment
.EXAMPLE
Set-OptimaBillAdjustment -OrganizationId 123 -Endpoint "us-3.rightscale.com" -RefreshToken "abc...123" -BillAdjustmentJSON "/path/to/adjustment.json"
.LINK
https://docs.rightscale.com/
.LINK
https://docs.rightscale.com/cm/dashboard/settings/account/enable_oauth
.LINK
https://docs.rightscale.com/api/general_usage.html
.LINK
https://reference.rightscale.com/bill_analysis/?url=swagger_adj.json
#>
[CmdletBinding()]

param(
    [Parameter(Position=0,mandatory=$true)]
    [Int]
    $OrganizationId,

    [Parameter(Position=1,mandatory=$true)]
    [ValidateSet("us-3.rightscale.com", "us-4.rightscale.com")]
    [String]
    $Endpoint,
    
    [Parameter(Position=2,mandatory=$true)]
    [String]
    $RefreshToken,
    
    [Parameter(Position=3,mandatory=$true)]
    [ValidateScript({
        if(-Not ($_ | Test-Path) ){
            throw "File or folder does not exist!"
        }
        if(-Not ($_ | Test-Path -PathType Leaf) ){
            throw "The Path argument must be a file! Folder paths are not allowed!"
        }
        if($_ -notmatch "(\.json)"){
            throw "The file specified in the path argument must be of type json!"
        }
        return $true 
    })]
    [System.IO.FileInfo]
    $BillAdjustmentJSON
)

try {
    $contentType = "application/json"
    $oAuthHeader = @{"X_API_VERSION" = "1.5" }
    $oAuthBody = @{
        "grant_type"    = "refresh_token";
        "refresh_token" = $RefreshToken
    } | ConvertTo-Json
    Write-Verbose "Retrieving access token..."
    $oAuthResult = Invoke-RestMethod -Uri "https://$Endpoint/api/oauth2" -Method Post -Headers $oAuthHeader -ContentType $contentType -Body $oAuthBody -UseBasicParsing -ErrorVariable responseError
    $accessToken = $oAuthResult.access_token

    if (-not($accessToken)) {
        Write-Warning "Error retrieving access token!"
        EXIT 1
    }

    Write-Verbose "Successfully retreived access token!"
    Write-Verbose "Setting Bill Adjustment..."

    $headers = @{
        "Api-Version" = "1.0";
        "Authorization" = "Bearer $accessToken"
    }

    $body = Get-Content -Path $BillAdjustmentJSON
    
    $response = Invoke-WebRequest -Uri "https://optima.rightscale.com/bill-analysis/orgs/$OrganizationId/adjustments/" -Method Put -Headers $headers -ContentType $contentType -Body $body -UseBasicParsing -ErrorVariable responseError
    if ($response.StatusCode -eq 204) {
        Write-Verbose "Bill Adjustment successfully set!"
    }
    else {
        Write-Warning "Error setting Bill Adjustments! Status Code: $($response.StatusCode)"
        Write-Warning $errorResponse
    }
}
catch {
    Write-Warning "Error setting Bill Adjustments! $($responseError | Out-String)"
}
