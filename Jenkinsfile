pipeline {
  agent any

  parameters {
    choice(name: 'INSTANCE_NUMBER', choices: ['1','2','3','4','5','6','7','8','9','10'], description: 'Instance')
  }

  environment {
    BASE_DIR    = 'C:\\ETL'  
    PROJECT_DIR = "${BASE_DIR}\\Project${params.INSTANCE_NUMBER}"
  }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {

    stage('Checkout this repo') {
      steps {
        checkout scm
      }
    }

    stage('Prepare dir') {
      steps {
        powershell '''
          New-Item -ItemType Directory -Force -Path "$env:PROJECT_DIR" | Out-Null
          Write-Host "WORKSPACE   = $env:WORKSPACE"
          Write-Host "PROJECT_DIR = $env:PROJECT_DIR"
        '''
      }
    }

    stage('Render settings.json') {
      steps {
        powershell '''
          $tplPath = Join-Path $env:WORKSPACE "settings.tpl.json"
          if (-not (Test-Path $tplPath)) { Write-Error "[FATAL] Template not found: $tplPath" }

          $tpl  = Get-Content $tplPath -Raw
          # Подставляем номер инстанса
          $json = $tpl -replace "\\$\\{INSTANCE_NUMBER\\}", "$env:INSTANCE_NUMBER"

          $out  = Join-Path $env:PROJECT_DIR "settings.json"
          # Пишем UTF-8 без BOM
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
          if (-not (Test-Path $venv)) {
            py -3 -m venv $venv
          }

          $pip = Join-Path $venv "Scripts\\pip.exe"
          $req = Join-Path $env:WORKSPACE "requirements.txt"

          & $pip install --upgrade pip
          if (Test-Path $req) {
            & $pip install -r $req
          } else {
            Write-Host "requirements.txt not found at $req — skipping"
          }
        '''
      }
    }

    stage('Run main.py (smoke)') {
      steps {
        powershell '''
          $proj = $env:PROJECT_DIR
          $py   = Join-Path $proj ".venv\\Scripts\\python.exe"
          $cfg  = Join-Path $proj "settings.json"
          $main = Join-Path $env:WORKSPACE "main.py"

          if (-not (Test-Path $cfg))  { Write-Error "[FATAL] settings.json not found: $cfg" }
          if (-not (Test-Path $py))   { Write-Error "[FATAL] Python not found in venv: $py" }
          if (-not (Test-Path $main)) { Write-Error "[FATAL] main.py not found: $main" }

          & $py $main --settings "$cfg"
        '''
      }
    }
  }
}
