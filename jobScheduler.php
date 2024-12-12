<?php

use job_cron\PostCreate;
require_once dirname(__DIR__).'/job_cron/PostCreate.php';

// ADDING CUSTOM INTERVAL
add_filter( 'cron_schedules', 'webapi_add_cron_interval' );
function webapi_add_cron_interval( $schedules ) {
    $schedules ['15_mins'] = array(
    'interval' => 900,
    'display' => esc_html__( 'Every Fifteen minutes' ), );
    return $schedules ;
}

// SETTING CUSTOM HOOK FOR WP CRON
add_action('job_cron_hook', 'job_cron_test');
function job_cron_test() {
    $jobs = new PostCreate;
    $jobs->get_jobs();
}

// TO PREVENT DUPLICATE EVENTS
if ( ! wp_next_scheduled( 'job_cron_hook' ) ) {
    wp_schedule_event( time(), '15_mins', 'job_cron_hook' );
}

//functions.php
//Comment job sync cron on staging and uncomment on live
// function comment_job_sync_on_staging() {
//     $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
//     $host = $_SERVER['HTTP_HOST'];
     
// 	 if($host == 'emerge360.com'){
// 	 require get_theme_file_path('/job_cron/jobScheduler.php');
//     }
// }
// comment_job_sync_on_staging();