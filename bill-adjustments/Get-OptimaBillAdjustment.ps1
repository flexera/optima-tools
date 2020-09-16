<#
.SYNOPSIS
Retrieves Flexera Optima Bill Adjustments.
.DESCRIPTION
This will retrieve a Bill Adjustment based on a provided name.
.PARAMETER OrganizationId
The Flexera CMP Organization Id.
.PARAMETER Endpoint
The Cloud Management endpoint for your account. Valid values: us-3.rightscale.com, us-4.rightscale.com
.PARAMETER RefreshToken
The users refresh token
.PARAMETER BillAdjustmentName
The name of the Bill Adjustment you would like to retrieve. If omitted, all Bill Adjustments are returned.
.PARAMETER SendToFile
The name of the file you would like to create with the Bill Adjustment data.
.PARAMETER PrettyPrint
Outputs the Bill Adjustment JSON to the console
.EXAMPLE
Get-OptimaBillAdjustment -OrganizationId 123 -Endpoint "us-3.rightscale.com" -RefreshToken "abc...123" -BillAdjustmentName "Foo Bar" -SendToFile "org123_adj.json"
.LINK
https://docs.rightscale.com/
.LINK
https://docs.rightscale.com/cm/dashboard/settings/account/enable_oauth
.LINK
https://docs.rightscale.com/api/general_usage.html
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
    
    [Parameter(Position=3,mandatory=$false)]
    [String]
    $BillAdjustmentName,

    [Parameter(Position=4,mandatory=$false)]
    [String]
    $SendToFile,

    [Parameter(Position=5,mandatory=$false)]
    [bool]
    $PrettyPrint = $true
)

try {
    $contentType = "application/json"
    $oAuthHeader = @{"X_API_VERSION" = "1.5" }
    $oAuthBody = @{
        "grant_type"    = "refresh_token";
        "refresh_token" = $RefreshToken
    } | ConvertTo-Json
    Write-Verbose "Retrieving access token..."
    $oAuthResult = Invoke-RestMethod -Uri "https://$Endpoint/api/oauth2" -Method Post -Headers $oAuthHeader -ContentType $contentType -Body $oAuthBody -ErrorVariable responseError
    $accessToken = $oAuthResult.access_token

    if (-not($accessToken)) {
        Write-Warning "Error retrieving access token!"
        EXIT 1
    }

    Write-Verbose "Successfully retreived access token!"
    Write-Verbose "Querying for Bill Adjustments..."

    $headers = @{
        "Api-Version" = "1.0";
        "Authorization" = "Bearer $accessToken"
    }
    
    $response = Invoke-RestMethod -Uri "https://optima.rightscale.com/bill-analysis/orgs/$OrganizationId/adjustments/" -Method Get -Headers $headers -ContentType $contentType -UseBasicParsing -ErrorVariable responseError
    if (-not($response)) {
        Write-Verbose "No Bill Adjustments found!"
    }
    else {
        Write-Verbose "Successfully retreived Bill Adjustments!"
        Write-Verbose "Filtering Bill Adjustments..."
        if(-not($BillAdjustmentName)) {
            Write-Verbose "No Bill Adjustment specified. Returning all!"
            if($SendToFile) {
                ($response | ConvertTo-Json -Depth 100) | Out-File $SendToFile
            }
            else {
                if($PrettyPrint) {
                    $response | ConvertTo-Json -Depth 100
                }
                else {
                    $response
                }
            }
        }
        elseif($response.dated_adjustment_lists.adjustment_list.name -contains $BillAdjustmentName) {
            Write-Verbose "Found Bill Adjustment!"
            $filteredResponse = $response.dated_adjustment_lists.adjustment_list | Where-Object { $_.name -eq $BillAdjustmentName}
            if($SendToFile) {
                ($filteredResponse | ConvertTo-Json -Depth 100) | Out-File $SendToFile
            }
            else {
                if($PrettyPrint) {
                    $filteredResponse | ConvertTo-Json -Depth 100
                }
                else {
                    $filteredResponse
                }
            }

        }
        else {
            Write-Verbose "Unable to find Bill Adjustment!"
        }
    }
}
catch {
    if($responseError -like "*(404) Not Found*") {
        Write-Verbose "Unable to find Bill Adjustment!"
    }
    else {
        Write-Warning "Error retrieving Bill Adjustments! $($responseError | Out-String)"
    }
}
