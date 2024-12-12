<?php

namespace job_cron;

class PostCreate
{

    public function __construct()
    {
        add_action('rest_api_init', [$this, 'register_job_api']);
    }

    /**
     * Register REST API route for receiving jobs.
     */
    public function register_job_api()
    {
        register_rest_route('job-cron/v1', '/receive-jobs', [
            'methods' => 'POST',
            'callback' => [$this, 'receive_jobs'],
            'permission_callback' => '__return_true',
        ]);
    }

    /**
     * Handle the received job data.
     */
    public function receive_jobs($request)
    {
        $data = json_decode($request->get_body());

        if (isset($data->jobsList)) {
            $this->webapi_create_jobs($data);
        }

        return rest_ensure_response(['status' => 'success', 'message' => 'Jobs processed successfully.']);
    }

    /**
     * Create or update job posts.
     */
    function webapi_create_jobs($data)
    {
        $category_id = get_cat_ID('Jobs');
        $f_path = STYLESHEETPATH . "/job_cron/data.json";

        if (file_exists($f_path)) {
            $file1 = fopen($f_path, "a");
        } else {
            $file1 = fopen($f_path, "w");
        }
        fwrite($file1, "DATE: " . date("F j, Y, g:i a") . "\n");

        foreach ($data->jobsList as $jobItem) {
            $post_id = $this->get_post_id_by_meta_key_and_value('jobid', $jobItem->jobid);

            if (empty($post_id)) {
                // add Post
                $jobpost_ = array(
                    'post_title'    => wp_strip_all_tags($jobItem->jobname),
                    'post_content'  => $jobItem->jobdescription,
                    'post_status'   => 'publish',
                    'post_author'   => get_current_user_id(),
                    'post_category' => array($category_id),
                    'post_date'     => $jobItem->jobdatecreated,
                    'post_modified' => $jobItem->jobdateupdated,
                );

                $postId = wp_insert_post($jobpost_);
                add_post_meta($postId, 'jobid', $jobItem->jobid);

                if (!empty($jobItem->featuredImageUrl)) {
                    $this->set_featured_image($postId, $jobItem->featuredImageUrl);
                }

                fwrite($file1, "Post Created, ID: " . $postId . "\t" . "Job-ID: " . $jobItem->jobid . "\n");
            } else {
                // Update the post
                $jobpost_ = array(
                    'post_title'    => wp_strip_all_tags($jobItem->jobname),
                    'post_content'  => $jobItem->jobdescription,
                    'post_status'   => 'publish',
                    'post_author'   => get_current_user_id(),
                    'post_category' => array($category_id),
                    'post_date'     => $jobItem->jobdatecreated,
                    'post_modified' => $jobItem->jobdateupdated,
                    'ID'            => $post_id,
                );

                $postId = wp_update_post($jobpost_);
                update_post_meta($postId, 'jobid', $jobItem->jobid);

                if ($jobItem->industryname != null) {
                    wp_add_post_tags($postId, $jobItem->industryname);
                } else {
                    wp_add_post_tags($postId, 'others');
                }

                add_post_meta($postId, 'job_country', $jobItem->countryname);

                // Upload and set the featured image
                if (!empty($jobItem->featuredImageUrl)) {
                    $this->set_featured_image($postId, $jobItem->featuredImageUrl);
                }

                fwrite($file1, "Post Updated, ID: " . $post_id . "\t" . "Job-ID: " . $jobItem->jobid . "\n");
            }
        }
        fwrite($file1, str_repeat("*", 53) . "\n");
        fclose($file1);
    }

    /**
     * Uploads an image from a URL and sets it as the featured image for a post.
     */
    function set_featured_image($post_id, $image_url)
    {
        $upload_dir = wp_upload_dir();

        $image_data = file_get_contents($image_url);
        if ($image_data === false) {
            return;
        }

        $filename = basename($image_url);
        $file_path = $upload_dir['path'] . '/' . $filename;

        file_put_contents($file_path, $image_data);

        $file_type = wp_check_filetype($filename, null);
        $attachment = array(
            'guid'           => $upload_dir['url'] . '/' . $filename,
            'post_mime_type' => $file_type['type'],
            'post_title'     => sanitize_file_name($filename),
            'post_content'   => '',
            'post_status'    => 'inherit',
        );

        $attachment_id = wp_insert_attachment($attachment, $file_path, $post_id);
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        $attachment_data = wp_generate_attachment_metadata($attachment_id, $file_path);
        wp_update_attachment_metadata($attachment_id, $attachment_data);

        set_post_thumbnail($post_id, $attachment_id);
    }

    /**
     * Get post ID by meta key and value.
     */
    function get_post_id_by_meta_key_and_value($key, $value)
    {
        global $wpdb;
        $meta = $wpdb->get_results($wpdb->prepare("SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s AND meta_value = %s", $key, $value));
        return $meta[0]->post_id ?? '';
    }
}

new PostCreate();
