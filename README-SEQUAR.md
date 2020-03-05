# SEQUAR SRL CONTRIBUTIONS

Our official custom branch is `11.0-sequar`.


## Updating/syncing with odoo base

1. Make sure this repository is `origin` remote.

    `git remote show origin` command should return
    
    ```
    Fetch URL: git@github.com:SequarSrl/odoo.git
    Push  URL: git@github.com:SequarSrl/odoo.git
    ```

    Otherwise you can remove current `origin` and adding the correct one.

    ```sh
    git remote remove origin
    git remote add origin git@github.com:SequarSrl/odoo.git
    ```

2. Add `upstream` remote from odoo official repository

    `git remote add upstream git@github.com:odoo/odoo.git`

3. Fetch changes from upstream

    `git fetch upstream`

4. Checkout `11.0` branch from `origin`

    `git checkout origin/11.0`

5. Merge `upstream` commits into current branch

    `git merge upstream/11.0`

6. Push updates to `origin` branch

    `git push origin HEAD:11.0`

7. Checkout `11.0-sequar` branch

    `git checkout 11.0-sequar`

8. Rebase `11.0-sequar` branch

    `git rebase -i origin/11.0`

8. Force push `11.0-sequar` branch to origin

    `git push -f origin 11.0-sequar`
