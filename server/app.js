const express = require('express');
const youtubeDl = require('youtube-dl-exec');
const ytDlp = youtubeDl.create('yt-dlp');
const yts = require("yt-search");
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

function sanitizeFilename(str) {
    return str.replace(/[^a-zA-Z0-9 ]/g, '_').replace(/\s+/g, '_');
}

app.get('/api/search', async (req, res) => {
    try {
        const query = req.query.q;
        if (!query) {
            return res.status(400).send({ error: 'Search query is required' });
        }

        const searchResults = await yts(query);
        return res.send(searchResults);
    } catch (error) {
        console.error('Search error:', error.message);
        return res.status(500).send({ error: 'Failed to search videos' });
    }
});

app.get('/api/video', async (req, res) => {
    try {
        const url = req.query.url;
        if (!url) {
            return res.status(400).send({ error: 'YouTube URL is required' });
        }

        const videoInfo = await ytDlp(url, {
            dumpSingleJson: true,
            noWarnings: true,
            format: 'bestvideo+bestaudio/best', // Fetch all available formats
        });

        const audioFormats = videoInfo.formats.filter(format =>
            format.acodec !== 'none' && format.vcodec === 'none'
        ).sort((a, b) => b.abr - a.abr);

        const videoFormats = videoInfo.formats.filter(format =>
            format.vcodec !== 'none' && format.acodec === 'none'
        ).sort((a, b) => b.height - a.height);

        const videoWithAudioFormats = videoInfo.formats.filter(format =>
            format.vcodec !== 'none' && format.acodec !== 'none'
        ).sort((a, b) => b.height - a.height);

        const data = {
            id: videoInfo.id,
            title: videoInfo.title,
            thumbnail: videoInfo.thumbnail,
            duration: videoInfo.duration,
            embed_url: `https://www.youtube.com/embed/${videoInfo.id}`,
            best_audio: audioFormats[0] || null,
            best_video: videoWithAudioFormats[0] || null,
            all_formats: videoInfo.formats
        };
        console.log('data :>> ', data);
        return res.json(data);
    } catch (error) {
        console.error('Video info error:', error.message);
        if (error.message.includes('Unable to download JSON metadata')) {
            return res.status(400).send({ error: 'Video not found or unavailable' });
        } else if (error.message.includes('Sign in to confirm your age')) {
            return res.status(403).send({ error: 'This video is age-restricted. Please provide authentication.' });
        } else {
            return res.status(500).send({ error: 'Failed to get video information' });
        }
    }
});

app.get('/api/download', async (req, res) => {
    const url = req.query.url;
    const format = req.query.format;
    const title = req.query.title;
    const ext = req.query.ext;

    if (!url || !format) {
        return res.status(400).send({ error: 'URL and format are required' });
    }

    try {
        let filename = 'video';
        if (title && ext) {
            filename = sanitizeFilename(title) + '.' + ext;
        } else {
            filename = 'video.mp4';
        }
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);

        const subprocess = ytDlp.exec(url, {
            format: format,
            output: '-',
        });

        subprocess.stdout.pipe(res);

        subprocess.on('error', (error) => {
            console.error('Download error:', error);
            if (!res.headersSent) {
                res.status(500).send({ error: 'Failed to download video' });
            }
        });

        subprocess.on('close', (code) => {
            if (code !== 0) {
                console.error(`yt-dlp exited with code ${code}`);
                if (!res.headersSent) {
                    res.status(500).send({ error: 'Failed to download video' });
                }
            }
        });
    } catch (error) {
        console.error('Download error:', error);
        res.status(500).send({ error: 'Failed to download video' });
    }
});

app.get('/', (req, res) => {
    res.send('API is running...');
}
);

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

// index.js
// const express = require('express');
// const ytdl = require('ytdl-core');
// const yts = require('yt-search');
// const cors = require('cors');
// const { PassThrough } = require('stream');

// const app = express();
// app.use(cors());
// app.use(express.json());

// function sanitizeFilename(str) {
//     return str.replace(/[^a-zA-Z0-9 ]/g, '_').replace(/\s+/g, '_');
// }

// // 1) SEARCH
// app.get('/api/search', async (req, res) => {
//     const q = req.query.q;
//     if (!q) return res.status(400).json({ error: 'Search query is required' });
//     try {
//         const result = await yts(q);
//         res.json(result);
//     } catch (err) {
//         console.error('Search error:', err);
//         res.status(500).json({ error: 'Search failed' });
//     }
// });

// // 2) VIDEO INFO
// app.get('/api/video', async (req, res) => {
//     const url = req.query.url;
//     if (!url || !ytdl.validateURL(url)) {
//         return res.status(400).json({ error: 'Valid YouTube URL is required' });
//     }

//     try {
//         const info = await ytdl.getInfo(url);

//         // All available formats
//         const allFormats = info.formats;

//         // Audio only (hasAudio && !hasVideo)
//         const audioFormats = allFormats
//             .filter(f => f.hasAudio && !f.hasVideo && f.url)
//             .sort((a, b) => (b.audioBitrate || 0) - (a.audioBitrate || 0));

//         // Video only (hasVideo && !hasAudio)
//         const videoFormats = allFormats
//             .filter(f => f.hasVideo && !f.hasAudio && f.url)
//             .sort((a, b) => (b.height || 0) - (a.height || 0));

//         // Video+Audio
//         const videoAudioFormats = allFormats
//             .filter(f => f.hasVideo && f.hasAudio && f.url)
//             .sort((a, b) => (b.height || 0) - (a.height || 0));

//         const baseData = {
//             id: info.videoDetails.videoId,
//             title: info.videoDetails.title,
//             thumbnail: info.videoDetails.thumbnails.slice(-1)[0].url,
//             duration: parseInt(info.videoDetails.lengthSeconds, 10),
//             embed_url: `https://www.youtube.com/embed/${info.videoDetails.videoId}`,
//             best_audio: audioFormats[0] || null,
//             best_video: videoAudioFormats[0] || null,  // combined is usually best
//             all_formats: allFormats
//         };

//         res.json(baseData);
//     } catch (err) {
//         console.error('Video info error:', err);
//         res.status(500).json({ error: 'Failed to retrieve video info' });
//     }
// });

// // 3) DOWNLOAD
// app.get('/api/download', async (req, res) => {
//     const url = req.query.url;
//     const format = req.query.format;  // this should be the format.itag
//     const title = req.query.title;
//     const ext = req.query.ext;

//     if (!url || !ytdl.validateURL(url) || !format) {
//         return res.status(400).json({ error: 'URL and format (itag) are required' });
//     }

//     // Sanitize filename
//     const safeTitle = title
//         ? sanitizeFilename(title)
//         : 'video';
//     const filename = ext
//         ? `${safeTitle}.${ext}`
//         : `${safeTitle}.mp4`;

//     res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
//     res.setHeader('Content-Type', 'application/octet-stream');

//     try {
//         // Create a passthrough so headers are set before piping
//         const stream = new PassThrough();
//         ytdl(url, { quality: format })
//             .pipe(stream)
//             .on('error', err => {
//                 console.error('Stream error:', err);
//                 if (!res.headersSent) {
//                     res.status(500).end('Download error');
//                 }
//             });

//         stream.pipe(res);
//     } catch (err) {
//         console.error('Download handler error:', err);
//         if (!res.headersSent) {
//             res.status(500).json({ error: 'Failed to download video' });
//         }
//     }
// });

// // Root health-check
// app.get('/', (_, res) => {
//     res.send('API is running...');
// });

// const PORT = process.env.PORT || 4000;
// app.listen(PORT, () => {
//     console.log(`Server listening on port ${PORT}`);
// });
