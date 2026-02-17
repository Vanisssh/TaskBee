<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Order;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class OrderController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = Order::query()->with(['service', 'client:id,name', 'specialist:id,user_id,rating_avg']);
        if ($request->has('status')) {
            $query->where('status', $request->string('status'));
        }
        $items = $query->orderByDesc('created_at')->get();
        return response()->json(['data' => $items]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'client_id' => 'required|exists:users,id',
            'service_id' => 'required|exists:services,id',
            'address' => 'nullable|string',
            'description' => 'nullable|string',
        ]);
        $validated['status'] = Order::STATUS_NEW;
        $order = Order::create($validated);
        $order->load(['service', 'client:id,name']);
        return response()->json(['data' => $order], 201);
    }

    public function show(Order $order): JsonResponse
    {
        $order->load(['service.category', 'client:id,name', 'specialist.user:id,name', 'review']);
        return response()->json(['data' => $order]);
    }

    public function update(Request $request, Order $order): JsonResponse
    {
        $validated = $request->validate([
            'specialist_id' => 'nullable|exists:specialists,id',
            'status' => 'sometimes|string|in:new,assigned,in_progress,completed,cancelled',
            'address' => 'nullable|string',
            'description' => 'nullable|string',
        ]);
        $order->update($validated);
        $order->load(['service', 'client:id,name', 'specialist:id,user_id,rating_avg']);
        return response()->json(['data' => $order]);
    }

    public function destroy(Order $order): JsonResponse
    {
        $order->delete();
        return response()->json(null, 204);
    }
}
