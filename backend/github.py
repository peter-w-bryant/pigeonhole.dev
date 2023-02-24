# Path: backend\github.py
import requests
import config
from datetime import datetime

class GitHubAPI:
    """GitHub API wrapper class"""
    def __init__(self, repo_url):
        try:
            self.repo_url = repo_url
            self.username = repo_url.split('/')[3]
            self.repo_name = repo_url.split('/')[4]
            self.base_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}"
            self.search_url = f"https://api.github.com/search/issues?q=repo:{self.username}/{self.repo_name}"
            self.auth_headers = {'Authorization': 'token ' + config.github_token}
            self.repo_data = requests.get(self.base_url, headers=self.auth_headers).json()

            # Get the data from GitHub API
            self.gh_description = self.get_repo_description()

            # Topics / tech stack
            self.gh_topics = [''] * 6 # empty list of 6 strings to store the topics
            self.gh_topics[:len(self.get_topics())] = self.get_topics() # get the topics

            # Issues / labels
            self.gh_issues_dict = self.get_issues()
            self.gh_issues = list(self.gh_issues_dict.keys())

            # Stars, forks, watchers count
            self.gh_stargazers_count = self.get_stargazers_count()
            self.gh_forks_count = self.get_forks_count()
            self.gh_watchers_count = self.get_watchers_count()

            # Date of last commit
            self.gh_date_of_last_commit = self.get_date_of_last_commit()

            # Data of last MERGED pull request
            self.gh_date_of_last_merged_pull_request = self.get_date_of_last_merged_pull_request()

            # Get CONTRIBUTING.md URL
            self.gh_contributing_url = self.get_contribute_url()

            # Generate New Contributor Score
            self.gh_new_contributor_score = self.generate_new_contributor_score()

        except Exception as e:
            print("Error in GitHubAPI INIT:", e)

    def verify_repo_url(self):
        """Verify if the repo url is valid"""
        try:
            if self.repo_data["message"] == "Not Found":
                return False
        except KeyError:
            return True

    def get_repo_description(self):
        """Get the repo description"""
        return self.repo_data["description"]

    def get_stargazers_count(self):
        """Get the number of stargazers (people who starred the repo)"""
        return self.repo_data["stargazers_count"]

    def get_forks_count(self):
        """Get the number of forks (people who forked the repo)"""
        return self.repo_data["forks_count"]

    def get_watchers_count(self):
        """Get the number of watchers (people who watched the repo)"""
        return self.repo_data["watchers_count"]

    def get_open_issues_count(self):
        """Get the number of open issues"""
        return self.repo_data["open_issues_count"]

    def get_topics(self):
        """Get the topics"""
        return self.repo_data["topics"]

    def get_date_of_last_commit(self):
        """Get the date of the last commit"""
        commits_json = requests.get(self.base_url + "/commits", headers=self.auth_headers).json()
        date_of_last_commit = commits_json[0]["commit"]["author"]["date"].split("T")[0]
        return date_of_last_commit

    def get_date_of_last_merged_pull_request(self):
        """Get the date of the last merged pull request"""
        try:
            pulls_json = requests.get(self.search_url + "+is:pr+is:merged", headers=self.auth_headers).json()
            date_of_last_merged_pull_request = pulls_json["items"][0]["closed_at"].split("T")[0]
        except Exception as e:
            print("Exception in get_date_of_last_merged_pull_request():", e)
        
        return date_of_last_merged_pull_request

    def get_issues(self):
        """Gets all the open issue labels and the counts of all issue labels for a given repository.

        Returns:
        issue_label_counts(dict): a dictionary with keys corresponding to unique issue labels whose values are the count
        of open issues that have that label tag.
        
        """
        issues_json = requests.get(self.base_url + "/issues", headers=self.auth_headers).json()
        issue_label_counts = {}
        for issue in issues_json:
            try:
                if issue['labels']:
                    for i in range(len(issue['labels'])):
                        if issue['labels'][i]['name'] not in issue_label_counts.keys():
                            issue_label_counts[issue['labels'][i]['name']] = 1
                        else:
                            issue_label_counts[issue['labels'][i]['name']] += 1
            except Exception as e:
                print(e)
                pass
        
        return self.get_issues_reorder_keys(issue_label_counts)
    
    def get_issues_reorder_keys(self, issue_dict):
        """Reorders a dictionary of issue label count pairs so that our most important issue
        tags appear first. In order of importance:
            good first issue
            up for grabs
            help wanted
            easy to fix
            beginner experience
            easy
            *if label contains 'starter' or 'begginer'

        Returns:
        resorted_issue_dict: the same issue dictionary passed but with keys in order of importance.
        """
        resorted_issue_dict = {}
        for key in ['good first issue', 'up-for-grabs', 'help wanted', 'easy to fix', 'beginner experience', 'easy']:
            if key in issue_dict.keys() or 'starter' in key or 'begginer' in key:
                resorted_issue_dict[key] = issue_dict[key]
        # add the rest of the keys
        for key in issue_dict.keys():
            if key not in resorted_issue_dict.keys():
                resorted_issue_dict[key] = issue_dict[key]

        return resorted_issue_dict

    def get_contribute_url(self):
        """Get the CONTRIBUTING.md url"""
        contribute_url = self.repo_data["html_url"] + "/blob/master/CONTRIBUTING.md"
        if requests.get(contribute_url).status_code == 404:
            return ""
        else:
            return contribute_url

    # TODO
    def generate_new_contributor_score(self):
        """Generate a new contributor score"""
        score = 0

        # Number of stars
        num_stars = self.gh_stargazers_count
        if 0 <= num_stars <= 5:
            score += 2
        elif 5 < num_stars <= 15:
            score += 1
        elif 15 < num_stars <= 30:
            score += 0.75
        elif 30 < num_stars <= 50:
            score += 0.5
        elif 50 < num_stars <= 100:
            score += 0.25
        elif 100 < num_stars <= 150:
            score += 0.1
    
        # Number of Forks
        num_forks = self.gh_forks_count
        if 0 <= num_forks <= 5:
            score += 2
        elif 5 < num_forks <= 15:
            score += 1
        elif 15 < num_forks <= 30:
            score += 0.5
        elif 30 < num_forks <= 50:
            score += 0.1

        # Contains CONTRIBUTING.md
        if self.gh_contributing_url != "":
            score += 3

        # Issue Labels
        for label in self.gh_issues:
            if label in ["good first issue", "up-for-grabs", "easy to fix", "easy"]:
                score += self.gh_issues_dict[label] * 0.1
            if label in ["help wanted"] or "beginner" in label:
                score += self.gh_issues_dict[label] * 0.05
        
        # Date of last merged PR
        date_last_pr = datetime.date(datetime.strptime(self.gh_date_of_last_merged_pull_request, "%Y-%m-%d")) 
        date_today = datetime.date(datetime.today())
        days_since_last_pr = abs((date_today - date_last_pr).days)
        if days_since_last_pr <= 7:
            score += 2
        elif 7 < days_since_last_pr <= 14:
            score += 1
        elif 14 < days_since_last_pr <= 30:
            score += 0.75
        elif 30 <= days_since_last_pr <= 60:
            score += 0.5

        return score

if __name__ == '__main__':
    # repo_url = 'https://github.com/up-for-grabs/up-for-grabs.net'
    repo_url = 'https://github.com/Bhupesh-V/defe'
    gh = GitHubAPI(repo_url)
    print(gh.get_contribute_url())
   
    

    

    