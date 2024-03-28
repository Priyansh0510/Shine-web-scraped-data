# Shine-web-scraped-data
To modularize your code and utilize YAML for configuration, follow these steps:

## Folder Structure
```
- config.yml
- script.py
- results/
  - scraped_platform_geolocation_datetime.csv
```

## Headlines for README.md
1. Introduction
2. Installation
3. Usage
4. Configuration
5. Results
6. Contributing
7. License

## Content for README.md
## 1. Introduction
This script scrapes job postings from Shine.com for data analyst positions. It extracts details such as company name, position, experience required, salary, location, profile name, posted time, skills, and job link. The script organizes the data into a DataFrame and saves it as a CSV file.

## 2. Installation
Ensure you have Python installed on your system. Clone this repository to your local machine. Install the required Python packages using pip:

```
pip install requests beautifulsoup4 pandas numpy PyYAML
```

## 3. Usage
Run the script `script.py`. Adjust the `base_url` and `num_pages` variables in the script to customize the scraping parameters.

## 4. Configuration
Configure the scraping parameters using the `config.yml` file:

```yaml
base_url: "https://www.shine.com/job-search/data-analyst-jobs?q=data-analyst"
num_pages: 3
```

## 5. Results
The scraped job data is saved as `scraped_platform_geolocation_datetime.csv` in the `results` directory. The CSV file contains columns for company name, position, experience, salary, location, profile name, posted time, skills, and job link.

## 6. Contributing
We welcome contributions to enhance the functionality and usability of this job scraping script. If you have any ideas for improvements, encounter bugs, or wish to add new features, please follow these steps:
- Fork the repository to your GitHub account.
- Create a new branch for your modifications: `git checkout -b feature/new-feature`
- Make your changes and ensure they align with the project's coding style and guidelines.
- Test your changes thoroughly.
- Commit your changes with descriptive commit messages: `git commit -m "Add new feature"`
- Push your changes to your fork: `git push origin feature/new-feature`
- Open a pull request detailing the changes you've made and any relevant information.
- Your pull request will be reviewed by the project maintainers, and once approved, it will be merged into the main branch.

Your contributions are valuable and help improve this project for everyone. Thank you for your interest and support!

## 7. License
This project is licensed under the [MIT License](LICENSE).
