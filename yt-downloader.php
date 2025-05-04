<?php
/*
Plugin Name: YT Downloader
Plugin URI: https://yourwebsite.com/yt-downloader
Description: Download YouTube videos directly from your WordPress dashboard.
Version: 1.0
Author: Muhammad Usman
Author URI: https://devusman.vercel.app/
License: GPL2
*/

// Hook to add menu
add_action('admin_menu', 'yt_downloader_menu');

function yt_downloader_menu() {
    add_menu_page(
        'YT Downloader',
        'YT Downloader',
        'manage_options',
        'yt-downloader',
        'yt_downloader_admin_page',
        'dashicons-download',
        100
    );
}

// Admin page callback
function yt_downloader_admin_page() {
    ?>
    <div class="wrap">
        <h1>YT Downloader</h1>
        <form method="post" action="">
            <input type="text" name="youtube_url" placeholder="Enter YouTube URL" style="width: 400px;" />
            <input type="submit" name="download_video" class="button button-primary" value="Download" />
        </form>
        <?php yt_handle_download(); ?>
    </div>
    <?php
}

// Register shortcode
add_shortcode('yt_downloader_html', 'yt_downloader_render_html');

function yt_downloader_render_html() {
    ob_start(); // Start output buffering

    $html_file = plugin_dir_path(__FILE__) . 'templates/index.html'; 

    if (file_exists($html_file)) {
        include($html_file);
    } else {
        echo "<p style='color: red;'>YT Downloader HTML file not found.</p>";
    }

    return ob_get_clean(); // Return the buffered content
}
