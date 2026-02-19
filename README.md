# ConnectX - Respectful Social Media Platform

## 🌟 Overview

ConnectX is a modern social media application built with Django that emphasizes respectful and safe community interactions. The platform features real-time toxic content detection, dynamic message curation, and comprehensive analytics dashboard.

### Key Features:

✅ **User Authentication** - Secure login and registration system
✅ **Feed & Posts** - Share text and image content with the community
✅ **Real-time Toxic Detection** - Instantly detect harmful language while typing
✅ **Smart Suggestions** - Get safer, respectful alternatives for toxic words
✅ **Like & Engage** - Interact with posts from the community
✅ **Analytics Dashboard** - View comprehensive statistics about community content
✅ **Modern UI** - Beautiful, responsive design with smooth animations
✅ **Mobile Friendly** - Works seamlessly on all devices

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual Environment (recommended)

### Installation

1. **Clone/Navigate to the project:**
```bash
cd c:\Users\kalim\Desktop\ConnectX
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install django pillow
```

4. **Apply migrations (already done):**
```bash
python manage.py migrate
```

5. **Create a superuser (already done):**
   - Username: `admin`
   - Password: `admin123`

6. **Run the development server:**
```bash
python manage.py runserver
```

7. **Access the application:**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

---

## 📱 Features Explained

### 1. Landing Page
- First page visitors see
- Quick login/register options
- Feature showcase

### 2. Authentication
- **Login Page**: Secure user login with validation
- **Register Page**: Create new account with email verification
- **Logout**: Safely exit the application

### 3. Feed Page
- View all posts from the community
- Search posts by content or username
- Filter by content type (text/images)
- Like/unlike posts
- View post details

### 4. Create Post
- Write and share content
- Add images to posts
- **Real-time Toxic Detection**: Detects harmful language as you type
- **Warnings**: Visual indicators for toxic content
- **Suggestions**: Get safer alternatives for toxic words
- Character counter (max 500 characters)

### 5. Toxic Content Detection
The system detects 20+ harmful words and provides alternatives:
- "hate" → "dislike"
- "stupid" → "uninformed"
- "idiot" → "person"
- "ugly" → "unconventional"
- And many more...

### 6. Analytics Dashboard
Comprehensive statistics showing:
- **Total Posts**: Overall community activity
- **Safe Posts**: Posts with respectful language
- **Toxic Posts**: Posts containing harmful language
- **Content Distribution**: Text vs. Image posts
- **Safety Score**: Platform health indicator
- **Top Contributors**: Most active users
- **Key Insights**: Actionable recommendations

---

## 🗂️ Project Structure

```
ConnectX/
├── accounts/                          # Main app
│   ├── models.py                      # Database models
│   ├── views.py                       # View logic
│   ├── urls.py                        # URL routing
│   ├── utils.py                       # Toxic detection utilities
│   ├── admin.py                       # Django admin config
│   ├── templates/accounts/            # HTML templates
│   │   ├── base.html                  # Base template
│   │   ├── landing.html               # Landing page
│   │   ├── login.html                 # Login page
│   │   ├── register.html              # Registration page
│   │   ├── feed.html                  # Feed page
│   │   ├── create_post.html           # Create post page
│   │   └── dashboard.html             # Analytics dashboard
│   ├── static/
│   │   └── accounts/
│   │       └── style.css              # App styles
│   └── migrations/                    # Database migrations
├── core/                              # Project settings
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # Project URL routing
│   ├── asgi.py                        # ASGI config
│   └── wsgi.py                        # WSGI config
├── media/                             # User uploaded files
├── static/                            # Static files
├── db.sqlite3                         # Database
└── manage.py                          # Django management

```

---

## 📊 Database Models

### Post Model
```python
- author (ForeignKey to User)
- content (TextField)
- image (ImageField, optional)
- created_at (DateTime)
- updated_at (DateTime)
- likes (ManyToMany to User)
- is_toxic (Boolean)
- toxic_score (Float 0-1)
```

### Comment Model
```python
- post (ForeignKey to Post)
- author (ForeignKey to User)
- content (TextField)
- created_at (DateTime)
- is_toxic (Boolean)
```

### ContentAnalytics Model
```python
- date (Date)
- total_posts (Integer)
- total_toxic_posts (Integer)
- total_safe_posts (Integer)
- text_posts (Integer)
- image_posts (Integer)
- avg_toxic_score (Float)
```

---

## 🔒 Toxic Content Detection

The detection system uses a keyword-based approach with severity levels:

### Severity Levels:
- **High**: Words like "hate", "stupid", "kill" (weight: 0.8)
- **Medium**: Words like "fool", "dumb", "ugly" (weight: 0.5)
- **Low**: Words like "dead", "boring", "weird" (weight: 0.2)

### Toxic Score Calculation:
```
Toxic Score = Sum of word weights / (word count × 2)
Result is normalized to 0-1 range
Content is flagged if score > 0.3
```

### User Feedback:
1. **Warning Icon** (⚠️): Indicates toxic content
2. **Severity Badge**: Shows level of toxicity
3. **Suggestion**: Provides a safer alternative

---

## 🎨 UI/UX Features

### Design Elements:
- **Color Scheme**: Purple gradient primary colors (#667eea, #764ba2)
- **Cards**: Elegant card-based layout with shadows
- **Responsive**: Mobile-first, works on all screen sizes
- **Smooth Animations**: Hover effects and transitions
- **Icons**: FontAwesome icons for intuitive navigation

### Interactive Elements:
- Real-time form validation
- Image preview before uploading
- Character counter for posts
- Like button with visual feedback
- Search and filter functionality
- Loading states

---

## 📈 Analytics Features

### Dashboard Shows:
- Overall community statistics
- Safe vs. Toxic content ratio
- Content type distribution
- Community health score
- Top active contributors
- Trend analysis
- Key insights and recommendations

### Calculations:
- Safety Score = (Safe Posts / Total Posts) × 100
- Toxicity Score = (Toxic Posts / Total Posts) × 100
- Average Toxic Score = Mean of all toxic_score values

---

## 🔐 Security Features

- CSRF protection on all forms
- Password hashing with Django's built-in system
- SQL injection prevention via ORM
- User authentication required for sensitive actions
- Admin access protected

---

## 🧪 Testing the Application

### Test Scenario 1: Create an Account
1. Visit http://127.0.0.1:8000/
2. Click "Create Account"
3. Fill in details:
   - Username: testuser
   - Email: test@example.com
   - Password: testpass123
4. Click Register

### Test Scenario 2: Create a Post (Safe)
1. Go to Feed
2. Click in the text area
3. Type: "I love this amazing platform!"
4. You should see a ✓ Green indicator (safe content)
5. Click Post

### Test Scenario 3: Create a Post (Toxic)
1. Go to Feed
2. Type: "This is stupid and I hate it"
3. You should see ⚠️ Red warning
4. System suggests: "This is uninformed and I dislike it"
5. Review the suggestion and proceed or edit

### Test Scenario 4: View Analytics
1. Click on "Analytics" in navigation
2. View community statistics
3. Check safe vs. toxic breakdown
4. See top contributors

---

## ⚙️ Configuration

### Settings to Modify (core/settings.py)

```python
# Database (default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static Files
STATIC_URL = '/static/'

# Timezone
TIME_ZONE = 'Asia/Kolkata'  # Change as needed
```

---

## 🚀 Deployment

For production deployment:

1. **Update Settings**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'your-secret-key-here'
   ```

2. **Collect Static Files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Use Production Server**:
   - Gunicorn: `gunicorn core.wsgi`
   - Waitress: `waitress-serve core.wsgi:application`

4. **Database Migration**:
   - Consider using PostgreSQL for production

5. **Environment Variables**:
   - Use .env files for sensitive data
   - Never commit secrets to version control

---

## 📝 API Endpoints

### Authentication
- `POST /login/` - User login
- `POST /register/` - User registration
- `GET /logout/` - User logout

### Posts
- `GET /feed/` - View all posts
- `POST /post/` - Create new post
- `GET/POST /post/<id>/delete/` - Delete post
- `GET /post/<id>/like/` - Toggle like

### Analytics
- `GET /dashboard/` - View analytics dashboard
- `POST /api/check-toxic/` - Check text for toxic content

---

## 🤝 Contributing

To improve ConnectX:

1. Add more toxic words to the detection system
2. Improve suggestion generation algorithm
3. Add comment functionality
4. Implement user profiles
5. Add email notifications
6. Create user blocking/reporting system
7. Add advanced analytics with graphs

---

## 📄 License

This project is open-source and available for educational purposes.

---

## 🆘 Troubleshooting

### Issue: "No module named 'django'"
**Solution**: Install Django: `pip install django pillow`

### Issue: "Posts not loading"
**Solution**: Run migrations: `python manage.py migrate`

### Issue: "Images not uploading"
**Solution**: Check media directory exists and has write permissions

### Issue: "Toxic detection not working"
**Solution**: Ensure utils.py is properly imported in views.py

### Issue: "Static files not loading"
**Solution**: Create `/static/` directory and run: `python manage.py collectstatic`

---

## 📞 Support

For issues or questions, review the code comments in:
- `accounts/views.py` - All view logic
- `accounts/utils.py` - Toxic detection
- `accounts/models.py` - Database structure

---

## 🎯 Future Roadmap

- [ ] Real AI-powered toxic detection (better-profanity library)
- [ ] User profiles with bio and avatar
- [ ] Comment system with nested replies
- [ ] Direct messaging between users
- [ ] Hashtag and mention support
- [ ] Advanced search and filtering
- [ ] User notifications system
- [ ] Content moderation tools for admins
- [ ] Report/blocking functionality
- [ ] Mobile app version
- [ ] Dark mode theme
- [ ] Export analytics as PDF

---

**Happy Posting! 🚀 Let's build a respectful community together!**
