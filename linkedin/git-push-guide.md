# Publish this repository to GitHub with Git

The project folder is already initialized as a local Git repository and has an initial commit (verify with `git status` and `git log --oneline`). To publish it:

1. On GitHub, create a new **public** repository named `stratax-analytics-portfolio`. Leave “Add a README,” `.gitignore`, and license unchecked because this folder already contains those files.
2. In a terminal, change directory into this folder.
3. Add the repository remote (replace `YOUR-USERNAME` with your GitHub username):

```bash
git remote add origin https://github.com/YOUR-USERNAME/stratax-analytics-portfolio.git
git push -u origin main
```

If you already added a remote, inspect it with `git remote -v` instead of adding a duplicate.

## If working from a different computer

Download and extract the ZIP, then open a terminal inside the extracted folder. If the `.git` directory is not included in your copy or download, create a new repository with `git init -b main`, then stage and commit the files before adding the remote.

## GitHub Pages (optional website)

The repository includes a static `index.html`. After publishing, open repository **Settings → Pages**, choose deployment from the `main` branch and `/ (root)`, then save. GitHub Pages may take a short time to publish; confirm the URL it provides before putting it on LinkedIn.
