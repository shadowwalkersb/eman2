def getJobType() {
    def causes = "${currentBuild.rawBuild.getCauses()}"
    def job_type = "UNKNOWN"
    
    if(causes ==~ /.*TimerTrigger.*/)    { job_type = "cron" }
    if(causes ==~ /.*GitHubPushCause.*/) { job_type = "push" }
    if(causes ==~ /.*UserIdCause.*/)     { job_type = "manual" }
    if(causes ==~ /.*ReplayCause.*/)     { job_type = "manual" }
    
    return job_type
}

def notifyGitHub(status) {
    if(JOB_TYPE == "push") {
        if(status == 'PENDING') { message = 'Building...' }
        if(status == 'SUCCESS') { message = 'Build succeeded!' }
        if(status == 'FAILURE') { message = 'Build failed!' }
        if(status == 'ERROR')   { message = 'Build aborted!' }
        step([$class: 'GitHubCommitStatusSetter', contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: "JenkinsCI/${JOB_NAME}"], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: message, state: status]]]])
    }
}

def notifyEmail() {
    if(JOB_TYPE == "push") {
        emailext(to: "$GIT_AUTHOR_EMAIL",  
                 subject: '[JenkinsCI/$PROJECT_NAME] ' + "($GIT_BRANCH_SHORT - ${GIT_COMMIT_SHORT})" + ' #$BUILD_NUMBER - $BUILD_STATUS!',
                 body: '''${SCRIPT, template="groovy-text.template"}''',
                 attachLog: true
                 )
    }
}

def isReleaseBuild() {
    return GIT_BRANCH ==~ /.*\/release.*/
}

def isContinuousBuild() {
    return GIT_BRANCH ==~ /.*\/master/
}

def isBinaryBuild() {
    def buildOS = ['linux': CI_BUILD_LINUX,
                   'mac':   CI_BUILD_MAC,
                   'win':   CI_BUILD_WIN
                  ]
    
    return (CI_BUILD == "1" || buildOS[SLAVE_OS] == "1")
}

def testPackage() {
    if(SLAVE_OS != 'win')
        sh "bash tests/test_binary_installation.sh ${INSTALLERS_DIR} eman2.${SLAVE_OS}.sh"
    else
        sh 'ci_support/test_wrapper.sh'
}

def deployPackage() {
    def installer_base_name = ['Centos6': 'centos6',
                               'Centos7': 'centos7',
                               'MacOSX' : 'mac',
                              ]
    if(isContinuousBuild()) {
        if(SLAVE_OS != 'win')
            sh "rsync -avzh --stats ${INSTALLERS_DIR}/eman2.${SLAVE_OS}.sh ${DEPLOY_DEST}/eman2." + installer_base_name[JOB_NAME] + ".unstable.sh"
        else
            bat 'ci_support\\rsync_wrapper.bat'
    }
}

def getHomeDir() {
    def result = ''
    if(SLAVE_OS == "win") {
        result = "${USERPROFILE}"
    }
    else {
        result = "${HOME}"
    }
    
    return result
}

pipeline {
  agent {
    node { label "${JOB_NAME}-slave" }
  }
  
  options {
    disableConcurrentBuilds()
    timestamps()
  }
  
  environment {
    JOB_TYPE = getJobType()
    GIT_BRANCH_SHORT = sh(returnStdout: true, script: 'echo ${GIT_BRANCH##origin/}').trim()
    GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'echo ${GIT_COMMIT:0:7}').trim()
    GIT_AUTHOR_EMAIL = sh(returnStdout: true, script: 'git log -1 --format="%ae"').trim()
    HOME_DIR = getHomeDir()
    INSTALLERS_DIR = '${HOME_DIR}/workspace/${JOB_NAME}-installers'
    DEPLOY_DEST    = 'zope@ncmi.grid.bcm.edu:/home/zope/zope-server/extdata/reposit/ncmi/software/counter_222/software_136/'

    CI_BUILD       = sh(script: "! git log -1 | grep '.*\\[ci build\\].*'",       returnStatus: true)
    CI_BUILD_WIN   = sh(script: "! git log -1 | grep '.*\\[ci build win\\].*'",   returnStatus: true)
    CI_BUILD_LINUX = sh(script: "! git log -1 | grep '.*\\[ci build linux\\].*'", returnStatus: true)
    CI_BUILD_MAC   = sh(script: "! git log -1 | grep '.*\\[ci build mac\\].*'",   returnStatus: true)
  }
  
  stages {
    // Stages triggered by GitHub pushes
    stage('notify-pending') {
      steps {
        notifyGitHub('PENDING')
        sh 'env | sort'
      }
    }
    
    stage('build-local') {
      when {
        not { expression { isBinaryBuild() } }
        expression { JOB_NAME != 'Win' }
      }
      
      steps {
        sh 'source $(conda info --root)/bin/activate eman-deps-9-gui && bash ci_support/build_no_recipe.sh'
      }
    }
    
    stage('build-recipe') {
      steps {
        sh 'bash ci_support/build_recipe.sh'
      }
    }
    
    stage('package') {
      when {
        expression { isBinaryBuild() }
      }
      
      steps {
        sh "bash ci_support/package.sh ${INSTALLERS_DIR} " + '${WORKSPACE}/ci_support/'
      }
    }
    
    stage('test-package') {
      when {
        expression {isBinaryBuild() }
      }
      
      steps {
        testPackage()
      }
    }
    
    stage('deploy') {
      when {
        expression {isBinaryBuild() }
      }
      
      steps {
        deployPackage()
      }
    }
  }
  
  post {
    success {
      notifyGitHub('SUCCESS')
    }
    
    failure {
      notifyGitHub('FAILURE')
    }
    
    aborted {
      notifyGitHub('ERROR')
    }
    
    always {
      notifyEmail()
    }
  }
}
