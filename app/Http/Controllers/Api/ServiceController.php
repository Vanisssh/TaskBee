<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Service;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ServiceController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $query = Service::query()->with('category');
        if ($request->has('category_id')) {
            $query->where('service_category_id', $request->integer('category_id'));
        }
        $items = $query->orderBy('name')->get();
        return response()->json(['data' => $items]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'service_category_id' => 'required|exists:service_categories,id',
            'name' => 'required|string|max:255',
            'description' => 'nullable|string',
        ]);
        $service = Service::create($validated);
        $service->load('category');
        return response()->json(['data' => $service], 201);
    }

    public function show(Service $service): JsonResponse
    {
        $service->load('category');
        return response()->json(['data' => $service]);
    }

    public function update(Request $request, Service $service): JsonResponse
    {
        $validated = $request->validate([
            'service_category_id' => 'sometimes|exists:service_categories,id',
            'name' => 'sometimes|string|max:255',
            'description' => 'nullable|string',
        ]);
        $service->update($validated);
        $service->load('category');
        return response()->json(['data' => $service]);
    }

    public function destroy(Service $service): JsonResponse
    {
        $service->delete();
        return response()->json(null, 204);
    }
}
