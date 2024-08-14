(roles_researcher_using_the_sre)=

# Using the Secure Research Environment

## {{newspaper}} Transferring files into or out of the SRE

Each time a request is made to bring data or software into ("ingress") or out of ("egress") the SRE, it needs to be reviewed in case it represents a security risk.
These reviews will be coordinated by the designated contact for your SRE.
They will have to discuss whether this is an acceptable risk to the data security with the project's principle investigator and data provider and the decision might be "no".

:::{hint}
You can make the process as easy as possible by providing as much information as possible about the code or data.
For instance, describing in detail what a dataset contains and how it will be use will help speed up decision making.
:::

## {{books}} Maintaining an archive of the project

:::{caution}
At the end of each project, the entire SRE is deleted.
:::

Anything that has not been transferred to the **/output/** folder to be considered for egress will be deleted forever at this point.

:::{important}
You are responsible for deciding what is worth archiving.
:::

While working on the project:

- store all your code in a **Gitea** repository.
- store all resources that might be useful to the rest of the project in the **/shared/** folder.
- store anything that might form an output from the project (_e.g._ images, documents or output datasets) in the **/output/** folder.

See {ref}`the section on sharing files <role_researcher_shared_storage>` to find out more about where to store your files.

## {{package}} Pre-installed applications

The workspace has several pre-installed applications and programming languages to help with your data analysis.

::::{admonition} Programming languages / compilers
:class: dropdown note

:::{include} snippets/software_languages.partial.md
:relative-images:
:::
::::

::::{admonition} Editors / IDEs
:class: dropdown note

:::{include} snippets/software_editors.partial.md
:relative-images:
:::
::::

::::{admonition} Writing / presentation tools
:class: dropdown note

:::{include} snippets/software_presentation.partial.md
:relative-images:
:::
::::

::::{admonition} Database access tools
:class: dropdown note

:::{include} snippets/software_database.partial.md
:relative-images:
:::
::::

::::{admonition} Other useful software
:class: dropdown note

:::{include} snippets/software_other.partial.md
:relative-images:
:::
::::

If you need anything that is not already installed, please discuss this with the designated contact for your SRE.

You can access applications from the desktop using either:

- the **Terminal** app accessible from the dock at the bottom of the screen
- via a drop-down menu when you right-click on the desktop or click the **{menuselection}`Applications`** button on the top left of the screen

:::{image} images/workspace_desktop_applications.png
:alt: How to access applications from the desktop
:align: center
:width: 90%
:::

A few specific examples are given below.

### {{woman_technologist}} VSCodium

You can start **VSCodium** from the **{menuselection}`Applications --> Development`** menu.

:::{image} images/workspace_desktop_vscodium.png
:alt: Running VSCodium
:align: center
:width: 90%
:::

### {{arrow_double_up}} R and RStudio

Typing `R` at the command line will give you a pre-installed version of **R**.

:::{image} images/workspace_terminal_r.png
:alt: Running R from a terminal
:align: center
:width: 90%
:::

Or you can use **RStudio** or **VSCodium** from the **{menuselection}`Applications --> Development`** menu.

:::{image} images/workspace_desktop_rstudio.png
:alt: Running RStudio
:align: center
:width: 90%
:::

### {{snake}} Python and Pycharm

Typing `python` at the command line will give you a pre-installed version of **Python**.

:::{image} images/workspace_terminal_python.png
:alt: Running Python from a terminal
:align: center
:width: 90%
:::

Or you can use **Pycharm** from the **{menuselection}`Applications --> Development`** menu.

:::{image} images/workspace_desktop_pycharm.png
:alt: Running RStudio
:align: center
:width: 90%
:::

## {{gift}} Installing software packages

You have access to packages from the **PyPI** and **CRAN** repositories from the SRE.
You can install packages you need from these copies in the usual way, for example `pip install` (Python) and `install.packages` (R).

Depending on the sensitivity level of your SRE, you may only have access to a subset of **R** and **Python** packages:

- {ref}`Tier 2 <policy_tier_2>` (medium security) environments have access to all packages on **PyPI** and **CRAN**.
- {ref}`Tier 3 <policy_tier_3>` (high security) environments only have pre-authorised packages available.

:::{tip}
If you need to use a package that is not on the allowlist see the section on how to [bring software or data into the environment](#-transferring-files-into-or-out-of-the-sre).
:::

### Python packages

:::{note}
You will not have permissions to install packages system-wide. We recommend using a **virtual environment**.

You can create one:

- using [VSCodium](https://code.visualstudio.com/docs/python/environments)
- using [PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)
- using **Python** [in a terminal](https://docs.python.org/3/library/venv.html)

:::

You can install **Python** packages into your virtual environment from a terminal.

:::{code} bash
> pip install NAME_OF_PACKAGE
:::

### R packages

:::{note}
You will not have permissions to install packages system-wide. You will need to use a **user package directory**.
:::

You can install **R** packages from inside **R** (or **RStudio**):

:::{code} R
> install.packages(NAME_OF_PACKAGE)
:::

You will see something like the following:

:::{code} R
Installing package into '/usr/local/lib/R/site-library'
(as 'lib' is unspecified)
Warning in install.packages("cluster") :
  'lib = "/usr/local/lib/R/site-library"' is not writable
Would you like to use a personal library instead? (yes/No/cancel)
:::

Type `yes`, which prompts you to confirm the name of the library:

:::{code} R
Would you like to create a personal library
'~/R/x86_64-pc-linux-gnu-library/4.1'
to install packages into? (yes/No/cancel)
:::

Type `yes` to install the packages.

(role_researcher_shared_storage)=

## {{open_file_folder}} Sharing files inside the SRE

There are several shared folder on each workspace that all collaborators within a research project team can see and access:

- [input data](#input-data): in the **/data/** folder
- [shared space](#shared-space): in the **/shared/** folder
- [output resources](#output-resources): in the **/output/** folder

<!-- - [scratch space](#scratch-space-scratch): `/scratch/` -->
<!-- - [backup space](#backup-space-backup): `/backup/` -->

### Input data

Data that has been approved and brought into the secure research environment can be found in the **/data/** folder.

- The contents of **/data/** will be identical on all workspaces in your SRE.
- Everyone working on your project will be able to access it.
- Everyone has **read-only access** to the files stored here.

If you are using the Data Safe Haven as part of an organised event, you might find additional resources in the **/data/** folder, such as example slides or document templates.

:::{important}
You will not be able to change any of the files in **/data/**.
If you want to make derived datasets, for example cleaned and reformatted data, please add those to the **/shared/** or **/output/** folders.
:::

### Shared space

The **/shared/** folder should be used for any work that you want to share with your group.

- The contents of **/shared/** will be identical on all workspaces in your SRE.
- Everyone working on your project will be able to access it
- Everyone has **read-and-write access** to the files stored here.

<!--
#### Scratch space: `/scratch/`

The `/scratch/` folder should be used for any work-in-progress that isn't ready to share yet.
Although everyone in your group will have **read-and-write access**, you can create your own folders inside `/scratch` and choose your own permissions for them.

:::{caution}
You should not use `/scratch/` for long-term storage as it can be reset at any time without warning (_e.g._ when the VM is restarted).
:::

The contents of `/scratch/` will be **different** on different VMs in your SRE.
-->

<!--
#### Backup space: `/backup/`

The `/backup/` folder should be used for any work-in-progress that you want to have backed up.
In the event of any data loss due to accidental data deletion by a TRE user, your system administrator can restore the `/backup/` folder to the state it was in at an earlier point in time (up to 12 weeks in the past).
This **cannot** be used to recover individual files - only the complete contents of the folder.
Everyone in your group will have **read-and-write access** to all folders on `/backup`.

The contents of `/backup/` will be **identical** on all workspaces in your SRE.
-->

### Output resources

Any outputs that you want to extract from the secure environment should be placed in the **/output/** folder on the workspace.

- The contents of **/output/** will be identical on all workspaces in your SRE.
- Everyone working on your project will be able to access it
- Everyone has **read-and-write access** to the files stored here.

Anything placed in here will be considered for data egress - removal from the secure research environment - by the project's principal investigator together with the data provider.

:::{tip}
You may want to consider having subfolders of **/output/** to make the review of this directory easier.
:::

## {{pill}} Version control using Gitea

**Gitea**[^footnote-gitea] is an open-source code hosting platform for version control and collaboration - similar to **GitHub**.
It allows you to use [git](https://git-scm.com/about) to **version control** your work, coordinate tasks using **issues** and review work using **pull requests**.

[^footnote-gitea]: **Gitea** is an open source project. We want to thank the community for maintaining free and open source software for us to use and reuse. You can read more about **Gitea** at [their website](<https://about.gitea.com/>).

The **Gitea** server within the SRE can hold code, documentation and results from your team's analyses.
Use the **Gitea** server to work collaboratively on code with other project team members.

:::{important}
This **Gitea** server is entirely within the SRE - you do not need to worry about the security of the information you upload there as it is inaccessible from the public internet.
:::

You can access **Gitea** from an internet browser in the workspace using the desktop shortcut.
Use your **{ref}`short-form username <roles_researcher_username>`** and **password** to login.

::::{admonition} Logging in to Gitea
:class: dropdown note

- Click the **{guilabel}`Sign in`** button on the top-right of the page.

    :::{image} images/gitea_homepage.png
    :alt: Gitea homepage
    :align: center
    :width: 90%
    :::

- Enter your **{ref}`short-form username <roles_researcher_username>`** and **password**.

    :::{image} images/gitea_login.png
    :alt: Gitea login
    :align: center
    :width: 90%
    :::

- Then click the **{guilabel}`Sign in`** button

::::

::::{admonition} Create a new repository
:class: dropdown note

- Log in to the **Gitea** dashboard

    :::{image} images/gitea_dashboard.png
    :alt: Gitea dashboard
    :align: center
    :width: 90%
    :::

- Click on the **{guilabel}`+`** button next to the **Repositories** label.

    :::{image} images/gitea_new_repository.png
    :alt: Clone Gitea project
    :align: center
    :width: 90%
    :::

- Fill out the required information, with the following guidelines:
    - leave **Make repository private** unchecked
    - leave **Initialize repository** checked

    :::{tip}
    When you make a repository inside the SRE "public" it is visible to your collaborators who also have access to the SRE but is still inaccessible to the general public via the internet.
    We recommend that you make your repositories public to facilitate collaboration within the secure research environment.
    :::

::::

::::{admonition} Work on an existing repository
:class: dropdown note

- Sign into **Gitea** and click the **{guilabel}`Explore`** button in the top bar.

    :::{image} images/gitea_explore.png
    :alt: Explore Gitea repositories
    :align: center
    :width: 90%
    :::

- Click on the name of the repository you want to work on.

    :::{image} images/gitea_repository_view.png
    :alt: View Gitea repository
    :align: center
    :width: 90%
    :::

- From the repository view, click the **{guilabel}`HTTP`** button and copy the URL using the copy icon.
- From the terminal, type the following command

    :::{code} bash
    git clone URL_YOU_COPIED_FROM_GITEA
    :::

- This will start the process of copying the repository to the folder you are using in the terminal.

    :::{note}
    In **git**, copying a project is known as "cloning".
    :::

::::

(roles_researcher_gitea_create_pull_request)=

::::{admonition} Create a pull request in Gitea
:class: dropdown note

- Before you start, you should have already created a branch and pushed your changes.
- From the repository view in **Gitea**, click the **{guilabel}`Pull requests`** button.
- Click the **{guilabel}`New Pull Request`** button on the right side of the screen.

    :::{image} images/gitea_pull_request_start.png
    :alt: Start Gitea pull request
    :align: center
    :width: 90%
    :::

- Select the source branch and the target branch then click the **{guilabel}`New Pull Request`** button.

    :::{image} images/gitea_pull_request_diff.png
    :alt: Choose pull request branches
    :align: center
    :width: 90%
    :::

- Add a title and description to your pull request then click the **{guilabel}`Create Pull Request`** button.

    :::{image} images/gitea_pull_request_finish.png
    :alt: Finalise Gitea pull request
    :align: center
    :width: 90%
    :::

- Your pull request is now ready to be approved and merged.
- For more information, check the **Gitea** [pull requests documentation](https://docs.gitea.com/next/usage/pull-request).

::::

## {{book}} Collaborative writing using HedgeDoc

**HedgeDoc**[^footnote-hedgedoc] is an open-source document hosting platform for collaboration - similar to **HackMD**.
It uses [Markdown](https://www.markdownguide.org/)[^footnote-markdown] which is a simple way to format your text so that it renders nicely in HTML.

[^footnote-hedgedoc]: **HedgeDoc** is an open source project. We want to thank the community for maintaining free and open source software for us to use and reuse. You can read more about **HedgeDoc** at [their website](<https://hedgedoc.org/>).

[^footnote-markdown]: If you've never used Markdown before, we recommend reading this [Markdown cheat sheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet).

The **HedgeDoc** server within the SRE can hold documents relating to your team's analyses.
Use the **HedgeDoc** server to work collaboratively on documents with other project team members.

:::{important}
This **HedgeDoc** server is entirely within the SRE - you do not need to worry about the security of the information you upload there as it is inaccessible from the public internet.
:::

You can access **HedgeDoc** from an internet browser from the workspace using the desktop shortcut.
Use your **{ref}`short-form username <roles_researcher_username>`** and **password** to login.

::::{admonition} Connecting to HedgeDoc
:class: dropdown note

- Click the **{guilabel}`Sign in`** button on the top-right of the page.

    :::{image} images/hedgedoc_homepage.png
    :alt: HedgeDoc homepage
    :align: center
    :width: 90%
    :::

- Enter your **{ref}`short-form username <roles_researcher_username>`** and **password**.

    :::{image} images/hedgedoc_login.png
    :alt: HedgeDoc login
    :align: center
    :width: 90%
    :::

- Then click the **{guilabel}`Sign in`** button

::::

::::{admonition} Editing other people's documents
:class: dropdown note

- When you create a Markdown document inside the SRE you decide on its access permissions.

    :::{image} images/hedgedoc_access_options.png
    :alt: HedgeDoc access options
    :align: center
    :width: 90%
    :::

- If you make your documents **editable**, your collaborators will be able to change the file.
- If you make your documents **locked**, your collaborators will be able to read but not edit the file.

    :::{note}
    The document can only be accessed by your collaborators inside the SRE, it is inaccessible from the public internet.
    ::::

::::

::::{admonition} Publishing your documents
:class: dropdown note

The default URL is quite long and difficult to share with your collaborators.
We recommend **publishing** the document to get a much shorter URL which is easier to share with others.

- Click the **{guilabel}`Publish`** button to publish the document and generate the short URL.
- Click the pen icon to return to the editable markdown view.

    :::{image} images/hedgedoc_publish.png
    :alt: Publish with HedgeDoc
    :align: center
    :width: 90%
    :::

    :::{important}
    Remember that the document is not published to the internet, it is only available to others within the SRE.
    :::
::::

## {{green_book}} Database access

Your project might use a database for holding the input data.
You might also/instead be provided with a database for use in analysing the data.
The database server will use either **Microsoft SQL** or **PostgreSQL**.

If you have access to one or more databases, you can access them using the following details, replacing _SRE\_URL_ with the {ref}`SRE URL <roles_researcher_sre_url>` for your project.

For guidance on how to use the databases, many resources are available on the internet.
Official tutorials for [MSSQL](https://learn.microsoft.com/en-us/sql/sql-server/tutorials-for-sql-server-2016?view=sql-server-ver16) and [PostgreSQL](https://www.postgresql.org/docs/current/tutorial.html) may be good starting points.

:::{admonition} Microsoft SQL server connection details
:class: dropdown note

- **Server name** : mssql._SRE\_URL_ (e.g. mssql.sandbox.projects.example.org)
- **Username**: databaseadmin
- **Password**: provided by your {ref}`System Manager <role_system_manager>`
- **Database name**: provided by your {ref}`System Manager <role_system_manager>`
- **Port**: 1433

:::

:::{admonition} PostgreSQL server connection details
:class: dropdown note

- **Server name**: postgresql._SRE\_URL_ (e.g. postgresql.sandbox.projects.example.org)
- **Username**: databaseadmin
- **Password**: provided by your {ref}`System Manager <role_system_manager>`
- **Database name**: provided by your {ref}`System Manager <role_system_manager>`
- **Port**: 5432

:::

Examples are given below for connecting using **DBeaver**, **Python** and **R**.
The instructions for using other graphical interfaces or programming languages will be similar.

### {{bear}} Connecting using DBeaver

#### Microsoft SQL

::::{admonition} 1. Create new Microsoft SQL server connection
:class: dropdown note

Click on the **{guilabel}`New database connection`** button (which looks a bit like an electrical plug with a plus sign next to it)

- Select **SQL Server** as the database type

    :::{image} images/db_dbeaver_select_mssql.png
    :alt: DBeaver select Microsoft SQL
    :align: center
    :width: 90%
    :::

::::

::::{admonition} 2. Provide connection details
:class: dropdown note

- **Host**: as above
- **Database**: as above
- **Authentication**: SQL Server Authentication
- **Username**: as above
- **Password**: as above
- Tick **Show All Schemas**
- Tick **Trust server certificate**

    :::{image} images/db_dbeaver_connect_mssql.png
    :alt: DBeaver connect with Microsoft SQL
    :align: center
    :width: 90%
    :::

::::

::::{admonition} 3. Download drivers if needed
:class: dropdown note

- After clicking finish, you may be prompted to download driver files even though they should be pre-installed.
- Click on the **{guilabel}`Download`** button if this happens.

    :::{image} images/db_dbeaver_driver_download.png
    :alt: DBeaver driver download for Microsoft SQL
    :align: center
    :width: 90%
    :::

- If drivers are not available contact your {ref}`System Manager <role_system_manager>`

::::

#### PostgreSQL

::::{admonition} 1. Create new PostgreSQL server connection
:class: dropdown note

Click on the **{guilabel}`New database connection`** button (which looks a bit like an electrical plug with a plus sign next to it)

- Select **PostgreSQL** as the database type

    :::{image} images/db_dbeaver_select_postgresql.png
    :alt: DBeaver select PostgreSQL
    :align: center
    :width: 90%
    :::

::::

::::{admonition} 2. Provide connection details
:class: dropdown note

- **Host**: as above
- **Database**: as above
- **Authentication**: Database Native
- **Username**: as above
- **Password**: as above

    :::{image} images/db_dbeaver_connect_postgresql.png
    :alt: DBeaver connect with PostgreSQL
    :align: center
    :width: 90%
    :::

::::

::::{admonition} 3. Download drivers if needed
:class: dropdown note

- After clicking finish, you may be prompted to download driver files even though they should be pre-installed.
- Click on the **{guilabel}`Download`** button if this happens.

    :::{image} images/db_dbeaver_driver_download.png
    :alt: DBeaver driver download for PostgreSQL
    :align: center
    :width: 90%
    :::

- If drivers are not available contact your {ref}`System Manager <role_system_manager>`

::::

### {{snake}} Connecting using Python

Database connections can be made using **pyodbc** (Microsoft SQL) or **psycopg2** (PostgreSQL).
The data can be read into a dataframe for local analysis.

::::{admonition} Microsoft SQL
:class: dropdown note

- Example of how to connect to the database server

    :::{code} python
    import pyodbc
    import pandas as pd

    # Connect to the database server
    server = "mssql.sandbox.projects.example.org"
    port = "1433"
    db_name = "master"
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};" + \
        f"SERVER={server},{port};" + \
        f"DATABASE={db_name};" + \
        "Trusted_Connection=yes;"
    )

    # Run a query and save the output into a dataframe
    df = pd.read_sql("SELECT * FROM information_schema.tables;", cnxn)
    print(df.head(3))
    :::
::::

::::{admonition} PostgreSQL
:class: dropdown note

- Example of how to connect to the database server

    :::{code} python
    import psycopg2
    import pandas as pd

    # Connect to the database server
    server = "postgresql.sandbox.projects.example.org"
    port = 5432
    db_name = "postgres"
    cnxn = psycopg2.connect(host=server, port=port, database=db_name)

    # Run a query and save the output into a dataframe
    df = pd.read_sql("SELECT * FROM information_schema.tables;", cnxn)
    print(df.head(3))
    :::
::::

### {{rose}} Connecting using R

Database connections can be made using **odbc** (Microsoft SQL) or **RPostgres** (PostgreSQL).
The data can be read into a dataframe for local analysis.

::::{admonition} Microsoft SQL
:class: dropdown note

- Example of how to connect to the database server

    :::{code} R
    library(DBI)
    library(odbc)

    # Connect to the database server
    cnxn <- DBI::dbConnect(
        odbc::odbc(),
        Driver = "ODBC Driver 17 for SQL Server",
        Server = "mssql.sandbox.projects.example.org,1433",
        Database = "master",
        Trusted_Connection = "yes"
    )

    # Run a query and save the output into a dataframe
    df <- dbGetQuery(cnxn, "SELECT * FROM information_schema.tables;")
    head(df, 3)
    :::
::::

::::{admonition} PostgreSQL
:class: dropdown note

- Example of how to connect to the database server

    :::{code} R
    library(DBI)
    library(RPostgres)

    # Connect to the database server
    cnxn <- DBI::dbConnect(
        RPostgres::Postgres(),
        host = "postgresql.sandbox.projects.example.org",
        port = 5432,
        dbname = "postgres"
    )

    # Run a query and save the output into a dataframe
    df <- dbGetQuery(cnxn, "SELECT * FROM information_schema.tables;")
    head(df, 3)
    :::
::::