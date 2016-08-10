## Prerender

### Configuring a Local Prerender Server for Development
#### Overview
The ROSIE bot relies on a Prerender server to "take a snapshot" of the crawled pages after AJAX calls of those pages are returned. In order to test and develop an effective crawler/scraper, a local Prerender server should be set up to work with the app server in order to generate the aforementioned snapshots.

The app server for osf.io runs on `localhost:5000` by default and the Prerender server runs on `localhost:3000` by default. In order for Prerender server to work with the app server, a middleware shall be configured. In case of developing for osf.io, since there are currently no drop-in middleware for Flask (the web app framework on which osf.io is built), Nginx shall be installed and configured to act as the middleware.

A simple illustration can be used to show how the Nginx middleware, app server and the Prerender server shall be configured to work together.


											  |----> Prerender (localhost:3000)
	HTTP Requests --> Nginx (localhost:80) ---
							  				  |----> osf.io (localhost:5000)

As seen in the graph, HTTP requests are made to the Nginx server, which would be dispatched to either the Prerender server or the app server, depending on the user agent string included in the header of each request. If the request includes a user agent string corresponding to a known spider, the request will be dispatched to the Prerender server. Otherwise, the request will be handled as a normal request by the osf.io server. Configurations could be made to Nginx to include different user agent strings for prerendering.

#### Steps for Configuration (for OS X)
##### Step I : Download Prerender
Prerender is an open-source app that renders the page with response of (some) AJAX calls on the page . It was originially designed for seach engine optimization and you can download it from its [GitHub repo](https://github.com/prerender/prerender). If you are using terminal, you may

	$ git clone https://github.com/prerender/prerender.git
	$ cd prerender
	$ npm install

The steps above will download the Prerender server source code from GitHub and install required dependencies. Under the same directory, you may start the server by

	$ node server.js

And in the terminal window you should see outputs showing the thread number of each instances and the port to which Prerender is listening (3000 by default)

	2016-06-01T13:10:46.891Z starting worker thread #0
	2016-06-01T13:10:46.903Z starting worker thread #1
	2016-06-01T13:10:46.906Z starting worker thread #2
	2016-06-01T13:10:46.909Z starting worker thread #3
	2016-06-01T13:10:47.641Z starting phantom...
	2016-06-01T13:10:47.659Z Server running on port 3000
	2016-06-01T13:10:47.664Z starting phantom...
	2016-06-01T13:10:47.683Z Server running on port 3000
	2016-06-01T13:10:47.690Z starting phantom...
	2016-06-01T13:10:47.729Z Server running on port 3000
	2016-06-01T13:10:47.747Z starting phantom...
	2016-06-01T13:10:47.761Z Server running on port 3000

To verify that Prerender works, you may open a browser and go to

	http://localhost:3000/http://localhost:5000

If Prerender is successfully installed and services for local osf.io development server are running, you should see an osf.io landing page without any static assets (e.g. pictures, css) loaded, along with many 504s in the output of the terminal of the Prerender server. This is because the domain of this particular request is `localhost:3000` instead of `localhost:5000`, causing the browser loading from urls that resolve to non-existent static assets. This problem will be solved once Nginx is installed and configured correctly.

Finally, type in the terminal

	export PRERENDER_SERVICE_URL=127.0.0.1:3000

to set the environment variable.


##### Step II : Download and Configure Nginx
Nginx is an HTTP server that may also serve as a reverse proxy server. We have mentioned that Nginx acts as a handler for HTTP requests. This is also true for HTTP responses.


									   |<---- Prerender (localhost:3000)
	Client <-- Nginx (localhost:80) --- HTTP Response
							  		   |<---- osf.io (localhost:5000)


As shown in the graph above, response from either the Prerender server or the osf.io app server will be handled by Nginx, who then return the response to the client. In other words, Nginx as a reverse proxy masks the distinction between a Prerender server and an osf.io app server. It serves as both a MUX and a DeMUX between clients (in this case, browsers and spiders) and app server(s).

To install Nginx, type in the terminal

	$ brew install nginx

Upon successful installation, `cd` to the directory where nginx is installed. On OS X, it is usually `/usr/local/etc/nginx`. Within this directory, open the `nginx.conf` file using a txt editor, you will see

	#Only showing content in "http" block without comments
	http {
	    include       mime.types;
	    default_type  application/octet-stream;

    	sendfile        on;
    	keepalive_timeout  65;
    	server {
    		listen       8080;
			server_name  localhost;

        	location / {
          	root   html;
            	index  index.html index.htm;
        	}

        	error_page   500 502 503 504  /50x.html;
        	location = /50x.html {
        		root   html;
        	}

    	}
    	include servers/*;
	}

Delete the entire "server" block which configures the default Nginx server, so that the file becomes

	#Only showing content in "http" block without comments
	http {
	    include       mime.types;
	    default_type  application/octet-stream;

    	sendfile        on;
    	keepalive_timeout  65;

    	include servers/*;
	}

Add the line `include /usr/local/etc/nginx/sites-enabled/*;` to the "http block" so that the configuration file will include files under the `/usr/local/etc/nginx/sites-enabled/` directory. The file becomes

	#Only showing content in "http" block without comments
	http {
	    include       mime.types;
	    include /usr/local/etc/nginx/sites-enabled/*;
	    default_type  application/octet-stream;

    	sendfile        on;
    	keepalive_timeout  65;

    	include servers/*;
	}

Save the file and exit. Within the same directory, type in the terminal

	$ mkdir sites-enabled
	$ cd sites-enabled

to create and enter the `/usr/local/etc/nginx/sites-enabled/` directory. Create a new file named `osf` in the directory. Copy and paste the following to the file

	server {
	    listen 80;
	    server_name 127.0.0.1;

	    proxy_buffering off;

	    root   /path/to/your/osf.io/root;
	    index  index.html;

	    location / {
	        try_files $uri @prerender;
	    }

	    location @prerender {
	        #proxy_set_header X-Prerender-Token YOUR_TOKEN;

	        set $prerender 0;
	        if ($http_user_agent ~* "rosiebot|baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot|vkShare|W3C_Validator") {
	            set $prerender 1;
	        }
	        if ($args ~ "_escaped_fragment_") {
	            set $prerender 1;
	        }
	        if ($http_user_agent ~ "Prerender") {
	            set $prerender 0;
	        }
	        if ($uri ~ "\.(js|css|xml|less|png|jpg|jpeg|gif|pdf|doc|txt|ico|rss|zip|mp3|rar|exe|wmv|doc|avi|ppt|mpg|mpeg|tif|wav|mov|psd|ai|xls|mp4|m4a|swf|dat|dmg|iso|flv|m4v|torrent|ttf|woff)") {
	            set $prerender 0;
	        }

	        #resolve using Google's DNS server to force DNS resolution and prevent caching of IPs
	        resolver 8.8.8.8;

	        if ($prerender = 1) {

	            #setting prerender as a variable forces DNS resolution since nginx caches IPs and doesnt play well with load balancing
	            set $prerender "127.0.0.1:3000";
	            rewrite .* /$scheme://$host$request_uri? break;
	            proxy_pass http://$prerender;
	        }
	        if ($prerender = 0) {
	            proxy_pass http://127.0.0.1:5000;
	        }
	    }
	}

For the line that says `root   /path/to/your/osf.io/root;`, change the path to the absolute path of your local osf.io repo, then save and exit.
Finally, `cd ..` to go back to the previous directory and type in the terminal

	$ sudo nginx -t

to test for errors in the configuration files. If no error exists,

	$ sudo nginx

Open the browser and go to `http://localhost` and you should be able to see the osf.io landing page and the development site is fully functional.

##### Step III : Make Sure Prerender Works
Recall that in the last step, we have set the configuration files for Nginx to include this snippet

	if ($http_user_agent ~* "rosiebot|baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot|vkShare|W3C_Validator") {
	            set $prerender 1;
	        }

That means Nginx will dispatch the request to the Prerender server if the user agent included in the header of each HTTP request is one of

	rosiebot|baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot|vkShare|W3C_Validator

To test that Prerender works for these user agent strings, install the Chrome plugin "User-Agent Switcher for Google Chrome". In the options menu, you may add the user agent string of "LinkedInBot", which is

	LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)

to create a new user agent. Switch to the newly created user agent and then visit any public project pages of `localhost` and you will get a static page in your browser if Nginx is configured correctly. You may also use the Chrome developer tools to see that the sources included are all static.
Note: ROSIEBot, whose user string is 'ROSIEBot/1.0 (+http://github.com/zamattiac/ROSIEBot)', may replace LinkedInBot

