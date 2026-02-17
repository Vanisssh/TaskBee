<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ServiceCategory;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ServiceCategoryController extends Controller
{
    public function index(): JsonResponse
    {
        $items = ServiceCategory::query()->orderBy('name')->get();
        return response()->json(['data' => $items]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'slug' => 'required|string|max:255|unique:service_categories,slug',
        ]);
        $category = ServiceCategory::create($validated);
        return response()->json(['data' => $category], 201);
    }

    public function show(ServiceCategory $category): JsonResponse
    {
        $category->load('services');
        return response()->json(['data' => $category]);
    }

    public function update(Request $request, ServiceCategory $category): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'slug' => 'sometimes|string|max:255|unique:service_categories,slug,' . $category->id,
        ]);
        $category->update($validated);
        return response()->json(['data' => $category]);
    }

    public function destroy(ServiceCategory $category): JsonResponse
    {
        $category->delete();
        return response()->json(null, 204);
    }
}
