if ((Get-Module -ListAvailable MicrosoftPowerBIMgmt) -eq $null) {
       Write-Host "PowerBI Management Module not found.." -ForegroundColor Red
       $Title = "Install Module?"
       $Message = "Would you like to install the latest Microsoft PowerBI Management Powershell modules?"
       $Yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "install the latest Microsoft PowerBI Management Powershell"
       $No = New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Exit this script"
       $Options = [System.Management.Automation.Host.ChoiceDescription[]]($Yes, $No)
       $Result = $Host.UI.PromptForChoice($Title, $Message, $Options, 0)
       Switch ($Result){
             0 {Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser}
             1 {[System.Windows.MessageBox]::Show('Error installing modules')}
             }
       }

Connect-PowerBIServiceAccount   # or Login-PowerBIServiceAccount

Try    {
    $WorkspaceIds = Get-PowerBIWorkspace | Select-Object -Property Id, Name | Sort-Object -Property Name | Out-GridView -PassThru -Title 'PowerBI Workspaces' 
}
Catch {
    [System.Windows.MessageBox]::Show($_,'PowerBI Workspaces',0,'Error')
}

foreach ($WorkspaceId in $WorkspaceIds) {
    Get-PowerBIReport -WorkspaceId $WorkspaceId.Id | Select-Object Id, Name | Foreach-Object { $Name = $_.Name  + ".pbix" -replace '\s', ''
        #Write-Output "Exporting Report $Name"
        Write-Progress -CurrentOperation "ExportingReport" ( "Exporting Report $Name ... " )
        #$Name = $name + ".pbix"
        Export-PowerBIReport -Id $_.Id -OutFile $_.Name
        Write-Progress -CurrentOperation "ExportingReport" ( "Exporting Report $Name ... Done" )
        #Write-Output "Exported Report $Name"
    }
} 
