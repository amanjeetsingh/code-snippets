# Code snippet to produce a list of regions where a set of services are available 
# Tested with PS version 5.1.19041.1237
# Input = a list of Providers which we wish to check across all Azure regions

$providerList = 'Microsoft.Purview','Microsoft.Storage','Microsoft.Network','Microsoft.KeyVault','Microsoft.Storage','Microsoft.DataFactory','Microsoft.Sql','Microsoft.Synapse','Microsoft.Databricks','Microsoft.EventHub'


# Create an array of regions where a given Provider is avaialable 
$result = @(Foreach ($i in $providerList)
{
    Get-AzLocation | Where-Object {$_.Providers -like $i} | Select-Object @{Name='Provider'; Expression={$i}},location
})


# Region master data; list of all the locations. This is master data of all regions available.
$locMaster = get-azlocation | select-object location

# Left outer join between location master data (locMaster) and provider-region array (result)
$loj = Join-Object -LeftObject $locMaster -RightObject $result -JoinType Left -On location

# Filter the results where all Providers are available 
$loj | group-object location | select-object -Property Count,Name | Where-Object Count -eq $providerList.Count

