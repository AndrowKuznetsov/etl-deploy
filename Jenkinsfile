pipeline {
  agent any
  parameters {
    choice(name: 'INSTANCE_NUMBER', choices: ['1','2','3','4','5','6','7','8','9','10'], description: 'Instance')
  }
  environment {
    BASE_DIR    = 'C:\\ETL'                                  
    PROJECT_DIR = "${env.BASE_DIR}\\Project${params.INSTANCE_NUMBER}"
  }
  stages {
    stage('Checkout this repo') { steps { checkout scm } }

    stage('Prepare dir') {
      steps {
        powershell 'New-Item -ItemType Directory -Force -Path "$env:PROJECT_DIR" | Out-Null'
      }
    }

    stage('Render settings.json') {
  steps {
    powershell '''
      $tpl  = Get-Content "$env:WORKSPACE\\settings.tpl.json" -Raw
      
      $json = $tpl -replace "\\$\\{INSTANCE_NUMBER\\}", "$env:INSTANCE_NUMBER"
      $out  = Join-Path $env:PROJECT_DIR "settings.json"

      
      [System.IO.File]::WriteAllText($out, $json, (New-Object System.Text.UTF8Encoding($false)))

      if (-not (Test-Path $out)) { Write-Error "[FATAL] settings.json not created at $out" }
      Get-Item $out | Format-List FullName,Length
    '''
  }
}


    stage('Create venv + install deps') {
      steps {
        powershell '''
          $venv = Join-Path $env:PROJECT_DIR ".venv"
          if (!(Test-Path $venv)) { py -3 -m venv $venv }
          $pip = Join-Path $venv "Scripts\\pip.exe"
          if (Test-Path "requirements.txt") {
            & $pip install --upgrade pip
            & $pip install -r requirements.txt
          }
        '''
      }
    }

    stage('Run main.py (smoke)') {
      steps {
        powershell '''
          $py = Join-Path (Join-Path $env:PROJECT_DIR ".venv") "Scripts\\python.exe"
          $env:SETTINGS_PATH = Join-Path $env:PROJECT_DIR "settings.json"
          & $py ".\\main.py"
        '''
      }
    }
  }
  options { timestamps(); disableConcurrentBuilds() }
}
