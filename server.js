const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const session = require('express-session');
const MongoDBStore = require('connect-mongodb-session')(session);
const path = require('path');

// Initialize Express App
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public'))); // Serve static files (HTML, CSS, JS)

// MongoDB Connection
mongoose.connect('mongodb+srv://asta:asta123@cluster0.6cqpx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
});
const db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', () => console.log('Connected to MongoDB'));

// Session Configuration
app.use(session({
    secret: '1eBdf3GonBT4Tjf6atFy67Ry', // Replace this with your own secret
    resave: false,
    saveUninitialized: false,
    store: new MongoDBStore({
        uri: 'mongodb+srv://asta:asta123@cluster0.6cqpx.mongodb.net/?retryWrites=true&w=majority',
        collection: 'sessions',
    }),
    cookie: { maxAge: 3600000 }, // Session expiry: 1 hour
}));

// User Schema & Model
const userSchema = new mongoose.Schema({
    name: String,
    email: String,
    password: String,
});
userSchema.pre('save', async function (next) {
    if (this.isModified('password')) {
        this.password = await bcrypt.hash(this.password, 10);
    }
    next();
});
const User = mongoose.model('User', userSchema);

// Routes
// Serve Home Page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'ai.html'));
});

// User Login
app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user || !(await bcrypt.compare(password, user.password))) {
        return res.status(401).send({ error: 'Invalid email or password' });
    }
    req.session.userId = user._id;
    res.send({ success: true });
});

// User Signup
app.post('/signup', async (req, res) => {
    const { name, email, password } = req.body;
    if (await User.findOne({ email })) {
        return res.status(400).send({ error: 'Email already exists' });
    }
    const user = new User({ name, email, password });
    await user.save();
    res.send({ success: true });
});

// Generate AI Text (Placeholder API)
app.post('/generate-text', async (req, res) => {
    const { prompt } = req.body;
    const responseText = `AI Response for: ${prompt}`; // Replace with actual AI logic or API integration
    res.json({ answer: responseText });
});

// Get User Info (Protected Route)
app.get('/get-user-info', async (req, res) => {
    if (!req.session.userId) return res.status(401).send({ error: 'Unauthorized' });
    const user = await User.findById(req.session.userId);
    res.json({
        username: user.name,
        email: user.email,
    });
});

// Start Server
const PORT = 3000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
