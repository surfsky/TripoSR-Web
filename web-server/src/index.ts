
import express from 'express';
import multer from 'multer';
import cors from 'cors';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import FormData from 'form-data';

const app = express();
const PORT = 3000;
const PYTHON_SERVICE_URL = 'http://localhost:8000/generate';

// Configure middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Configure storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = 'public/uploads';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ storage });

// Routes
app.post('/api/upload', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No image uploaded' });
        }

        const imagePath = req.file.path;
        console.log(`Processing image: ${imagePath}`);

        // Get additional parameters from request body
        const { mc_resolution, foreground_ratio, do_remove_background } = req.body;

        // Prepare form data for Python service
        const formData = new FormData();
        formData.append('file', fs.createReadStream(imagePath));
        if (mc_resolution) formData.append('mc_resolution', mc_resolution);
        if (foreground_ratio) formData.append('foreground_ratio', foreground_ratio);
        if (do_remove_background !== undefined) formData.append('do_remove_background', do_remove_background);

        // Call Python service
        console.log('Calling Python service...');
        const response = await axios.post(PYTHON_SERVICE_URL, formData, {
            headers: {
                ...formData.getHeaders()
            },
            responseType: 'arraybuffer'
        });

        // Save generated model
        const modelsDir = 'public/models';
        if (!fs.existsSync(modelsDir)) {
            fs.mkdirSync(modelsDir, { recursive: true });
        }

        const modelFilename = `model-${Date.now()}.glb`;
        const modelPath = path.join(modelsDir, modelFilename);
        
        fs.writeFileSync(modelPath, response.data);
        console.log(`Model saved to: ${modelPath}`);

        // Return URLs
        res.json({
            success: true,
            imageUrl: `http://localhost:${PORT}/${req.file.path.replace('public/', '')}`,
            modelUrl: `http://localhost:${PORT}/models/${modelFilename}`
        });

    } catch (error: any) {
        console.error('Error processing request:', error.message);
        res.status(500).json({ 
            error: 'Failed to process image',
            details: error.message 
        });
    }
});

app.listen(PORT, () => {
    console.log(`Web server running on http://localhost:${PORT}`);
});
