# Adhoc Deployments via Zuul CI

## 1.0 Pre-requisites

**Important** before doing any other setup work you should ensure that your GitHub organisation has been setup with the Zuul CI app profile.

1. Navigate to the Zuul app install link 
2. Select your organisation from the list:
3. Finally select "Install" to complete the process.
4. Ensure the github user `pipeline-user` has been given write access to your code git repo in order for it to raise PR's.

### 1.1 Initial Setup PRs

Please make sure you have merged the required PRs that get automatically generated for you when you onboard your feature onto the Smart Pipeline:

The Zuul tenant PR should be sent to CDE for approval and upon it being merged, a CI job will automatically publish the new configuration.


### 1.2 Branch Protection

For best practices and for the full Zuul experience, make sure to enable branch protection on your `master` branch of your code repo:

1. Visit the repo setting page for your feature:
2. If you have a rule for `master` then select "Edit" for the `master` branch else create a new one for `master` and enable these options:
   - "Require pull request reviews before merging"
   - "Dismiss stale pull request approvals when new commits are pushed"
   - "Require status checks to pass before merging"
   - "Require branches to be up to date before merging"

### 1.3 Other Steps for Existing SMP Features

If your feature is already present within the Smart Pipeline make sure that you have `platform: PLATFORM` set within your `pipeline.yml` file.