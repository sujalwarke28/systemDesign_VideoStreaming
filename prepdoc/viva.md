# VIVA Questions & Answers

This document contains a curated list of questions ranging from Beginner to Advanced that an examiner might ask during your VIVA presentation.

---

## Core System Design Questions

**Q: Why are videos stored in object storage rather than databases?**
**Answer**: Better scalability, lower cost, and support for large binary files.

**Q: What is video transcoding?**
**Answer**: Converting uploaded videos into multiple formats and resolutions.

**Q: Why use adaptive bitrate streaming?**
**Answer**: Provides optimal playback quality based on network conditions.

**Q: How does CDN improve performance?**
**Answer**: Serves content from edge locations closer to users.

**Q: How would you handle viral videos?**
**Answer**: Edge caching, CDN replication, and auto-scaling.

---

## Beginner Level

**Q1: What technologies did you use for the frontend and why?**
**Answer**: I used HTML5, Vanilla JavaScript, and Bootstrap 5. I chose Bootstrap because it provides responsive, pre-built components (like the navigation bar and grid system) that drastically reduce CSS development time. I used Vanilla JS with the Fetch API because it's lightweight and doesn't require compiling, unlike React or Angular.

**Q2: What is the purpose of the `venv` folder in your project?**
**Answer**: `venv` stands for Virtual Environment. It isolates the Python dependencies used in this specific project from the global Python installation on my computer. This ensures that versions of libraries (like FastAPI or Motor) do not clash with other projects.

**Q3: Where is the database located?**
**Answer**: The database is hosted on MongoDB Atlas, which is a fully managed cloud NoSQL database service. 

**Q4: How does a user register an account?**
**Answer**: The user submits their username, email, and password via the frontend form. The Javascript intercepts the submission, packages the data into JSON, and sends an HTTP POST request to the `/auth/register` endpoint. The backend hashes the password using bcrypt and saves the document in MongoDB.

**Q5: How did you implement icons in the project without using image files?**
**Answer**: I used Bootstrap Icons, which are SVGs (Scalable Vector Graphics) injected via CSS classes (e.g., `bi-play-btn-fill`). I also used a Data URI (`data:image/svg+xml`) directly inside the `<link rel="icon">` tag to render an SVG as the browser tab favicon without needing an external `.ico` file.

---

## Intermediate Level

**Q5: Why did you choose FastAPI over Flask or Django?**
**Answer**: FastAPI is natively asynchronous, whereas Flask and Django (traditionally) are synchronous. Because video streaming requires holding many connections open simultaneously to transmit data, an asynchronous framework is crucial so the server doesn't block other requests while reading a file from the disk.

**Q6: How does your authentication system work?**
**Answer**: It uses JSON Web Tokens (JWT). When a user logs in successfully, the backend creates a JSON object with their user ID, signs it with a secret key, and sends it back. The frontend saves this token in `localStorage`. For any protected action (like uploading or liking), the frontend attaches this token to the `Authorization` header.

**Q7: Why use NoSQL (MongoDB) instead of a relational database like MySQL?**
**Answer**: Video platforms have highly flexible and evolving schemas (e.g., arrays of tags, varying metadata). MongoDB's document-based structure handles arrays and nested data perfectly without needing complex bridging tables. Furthermore, NoSQL databases scale horizontally much easier than relational databases.

**Q8: How did you implement the "Trending" logic?**
**Answer**: Every time a user clicks on a video, the `views` integer inside the MongoDB video document is incremented. The backend `GET /videos/trending` endpoint simply queries the database and sorts the results by the `views` field in descending order (`-1`).

**Q9: How did you replace native browser alerts with custom Toast notifications?**
**Answer**: I created a single hidden Bootstrap Toast container in the `base.html` template. I wrote a global JavaScript function `showToast(message, type)` that selects this container, updates its inner text, dynamically adds context color classes (like `bg-success` for success, `bg-danger` for errors), and triggers Bootstrap's fade-in animation using JavaScript. This provides a non-blocking, modern user experience compared to `alert()`.

---

## Advanced Level

**Q9: How exactly do you stream the video without crashing the server's memory?**
**Answer**: I implemented HTTP Range Requests combined with a CDN. Instead of reading the entire file into the EC2 server's RAM, the HTML5 video player requests the video from our CloudFront CDN. CloudFront intercepts the `Range` header sent by the browser, seeks to that exact byte offset in its edge cache (or from S3), reads a small chunk, and sends it back with an HTTP `206 Partial Content` status. This completely offloads the streaming burden from the backend API.

**Q10: What is Denormalization, and where did you use it?**
**Answer**: Denormalization is a database optimization technique where redundant data is added to a document to improve read performance. I used it in the Video model. Instead of just saving the `creator_id` and performing an expensive lookup to find the user's name every time the homepage loads, I save the `creator_name` directly in the Video document when it is uploaded.

**Q11: How do you handle file storage in this project, and how would you change it for a production environment at scale?**
**Answer**: The backend API is hosted on an AWS EC2 instance, but the media files themselves are stored in a highly scalable AWS S3 Object Storage bucket. To prevent disk I/O bottlenecks and minimize latency, a Content Delivery Network (AWS CloudFront) sits in front of the S3 bucket to cache and stream the videos globally from edge locations.

**Q12: How does the Jinja2 templating engine work in your architecture?**
**Answer**: Instead of building an entirely separate Single Page Application (SPA), FastAPI uses Jinja2 to dynamically generate HTML on the server. When a user requests the `/history` route, the backend injects variables like `page_title` and `api_endpoint` into the `index.html` template. The server compiles this into pure HTML and sends it to the browser. This allows me to reuse the same layout for different pages seamlessly.
