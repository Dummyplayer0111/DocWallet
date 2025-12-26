1.Create a new folder and inside it follow the other steps.

2.Make sure python is accessible there by opening a commaand prompt there and using the command "python --version" or "python3 --version".

3.If it is accessible create a new virtual environment using the command "python -m venv venv".

4.Inside the same folder clone the repository and open command prompt in the repository folder.Type the command "pip install -r requirements.txt" to install all required dependencies

5.The folder should look like this:
	->DocWallet
	       ->venv
	       ->Docwallet
		      ->DocWallet
		      ->Category_Handler
		      ->Login_Handler
		      ->.gitignore
		      ->db.sqlite3
		      ->readme.txt
		      ->requirements.txt
	      	      ->requirements.txt
		      ->manage.py
		      (Open command prompt here)

6.Go to google cloud console create a new project and set up an OAuth external client with the following scopes and add a few audiences:
	auth/drive.appdata
	auth/userinfo.email
Make sure to include authorised redirect URLS and authorised javascript origins as those of localhost. 

7.In DocWallet/DocWallet/DocWallet create a new '.env' file and put in the following:

	GOOGLE_OAUTH_CLIENT_ID='Your OAuth Client's ID here'
	GOOGLE_OAUTH_CLIENT_SECRET='Your OAuth Client's secret here'
	SECRET_KEY='Django Secret Key here'

8.Now navigate to DocWallet/Docwallet on command prompt and run the following command 'python manage.py runserver'

9.The server will run and you can use the app you need internet to use it.Press 'Ctrl+C' to stop the server.

10.To use the web-app go to localhost:8000 or 127.0.0.1:8000 on a browser.

