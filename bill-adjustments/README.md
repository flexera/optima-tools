# Optima Bill Adjustment Scripts

## Helpful Information

* Links
  * [How to get a Refresh Token](https://docs.rightscale.com/cm/dashboard/settings/account/enable_oauth)
    * Note 1: Refresh Tokens are specific to a user/shard, NOT an account. You technically only need one for US-3 and US-4.
    * Note 2: Treat refresh tokens as passwords/secrets. They are sensitive and specific to you.
  * [Bill Adjustments API Reference](https://reference.rightscale.com/bill_analysis/?url=swagger_adj.json)
  * [COS Enablement Confluence Document](https://confluence.flexera.com/display/rightscale/COS+Adjustment+Enablement)
  * [Bill Adjustment JSON Editor](https://reference.rightscale.com/bill_analysis/adj_json_editor/)
* Information
  * By default, these scripts are designed to run with little to no feedback. Add `-Verbose` to the end of any command to get more detailed information.
  * If copying from your web browser, make sure to click the `Raw` button before copying.

For macOS users, install PowerShell with brew:
```
$ brew cask install powershell
```
Then you can start a session: `pwsh`

## [Get-OptimaBillAdjustment.ps1](Get-OptimaBillAdjustment.ps1)

To get all Bill Adjustments in an Org:

```powershell
$orgId = 123
$endpoint = "us-3.rightscale.com"
$refreshToken = "abc...123"
./Get-OptimaBillAdjustment.ps1 -OrganizationId $orgId -Endpoint $endpoint -RefreshToken $refreshToken
```

To get a Bill Adjustment based on name:

```powershell
$orgId = 123
$endpoint = "us-3.rightscale.com"
$refreshToken = "abc...123"
$name = "Foo Bar"
./Get-OptimaBillAdjustment.ps1 -OrganizationId $orgId -Endpoint $endpoint -RefreshToken $refreshToken -BillingAdjustmentName $name
```

To send the Bill Adjustment to a file for future reference:

```powershell
$orgId = 123
$endpoint = "us-3.rightscale.com"
$refreshToken = "abc...123"
$outputJSON = "org-123_bill_adj.json"
./Get-OptimaBillAdjustment.ps1 -OrganizationId $orgId -Endpoint $endpoint -RefreshToken $refreshToken -SendToFile $outputJSON

```

To output the Bill Adjustment as a PowerShell object:

```powershell
$orgId = 123
$endpoint = "us-3.rightscale.com"
$refreshToken = "abc...123"
$outputJSON = "org-123_bill_adj.json"
./Get-OptimaBillAdjustment.ps1 -OrganizationId $orgId -Endpoint $endpoint -RefreshToken $refreshToken -PrettyPrint $false

```

## [Set-OptimaBillAdjustment.ps1](Set-OptimaBillAdjustment.ps1)

**To set a Bill Adjustment, you will need to already have generated the JSON file!**

To replace all Bill Adjustments in the org:

```powershell
$orgId = 123
$endpoint = "us-3.rightscale.com"
$refreshToken = "abc...123"
$inputJSON = "path/to/file.json"
./Set-OptimaBillAdjustment.ps1 -OrganizationId $orgId -Endpoint $endpoint -RefreshToken $refreshToken -BillAdjustmentJSON $inputJSON
```
