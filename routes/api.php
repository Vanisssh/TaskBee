<?php

use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function () {
    Route::apiResource('categories', \App\Http\Controllers\Api\ServiceCategoryController::class);
    Route::apiResource('services', \App\Http\Controllers\Api\ServiceController::class);
    Route::apiResource('orders', \App\Http\Controllers\Api\OrderController::class);
    Route::apiResource('reviews', \App\Http\Controllers\Api\ReviewController::class);
});
