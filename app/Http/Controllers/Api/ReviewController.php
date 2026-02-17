<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Order;
use App\Models\Review;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ReviewController extends Controller
{
    public function index(): JsonResponse
    {
        $items = Review::query()->with(['order:id,service_id', 'user:id,name'])->orderByDesc('created_at')->get();
        return response()->json(['data' => $items]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'order_id' => 'required|exists:orders,id',
            'user_id' => 'required|exists:users,id',
            'rating' => 'required|integer|min:1|max:5',
            'comment' => 'nullable|string',
        ]);
        $order = Order::findOrFail($validated['order_id']);
        if ($order->status !== Order::STATUS_COMPLETED) {
            return response()->json(['message' => 'Отзыв можно оставить только по выполненному заказу.'], 422);
        }
        $review = Review::create($validated);
        $review->load(['order', 'user:id,name']);
        return response()->json(['data' => $review], 201);
    }

    public function show(Review $review): JsonResponse
    {
        $review->load(['order.service', 'user:id,name']);
        return response()->json(['data' => $review]);
    }

    public function update(Request $request, Review $review): JsonResponse
    {
        $validated = $request->validate([
            'rating' => 'sometimes|integer|min:1|max:5',
            'comment' => 'nullable|string',
        ]);
        $review->update($validated);
        $review->load(['order', 'user:id,name']);
        return response()->json(['data' => $review]);
    }

    public function destroy(Review $review): JsonResponse
    {
        $review->delete();
        return response()->json(null, 204);
    }
}
