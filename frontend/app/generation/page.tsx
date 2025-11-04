"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { characterApi, generationApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Video, Play, Clock, CheckCircle, XCircle } from "lucide-react";

export default function GenerationPage() {
  const queryClient = useQueryClient();
  const [selectedCharacter, setSelectedCharacter] = useState<number | null>(null);
  const [prompt, setPrompt] = useState("");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [quality, setQuality] = useState("low");

  const { data: characters } = useQuery({
    queryKey: ["characters"],
    queryFn: async () => {
      const response = await characterApi.getAll();
      return response.data;
    },
  });

  const { data: generations, isLoading } = useQuery({
    queryKey: ["generations"],
    queryFn: async () => {
      const response = await generationApi.getAll();
      return response.data;
    },
  });

  const generateMutation = useMutation({
    mutationFn: (data: any) => generationApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generations"] });
      setPrompt("");
    },
  });

  const handleGenerate = () => {
    generateMutation.mutate({
      generation_type: "text_to_video",
      prompt,
      aspect_ratio: aspectRatio,
      quality,
      character_id: selectedCharacter,
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "processing":
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Video Generation</h1>
        <p className="text-muted-foreground">
          Generate videos with Veo 3.1 using text, image, or video prompts
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>New Generation</CardTitle>
              <CardDescription>Configure and start a new video generation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Prompt</label>
                <textarea
                  className="w-full px-3 py-2 border rounded-md min-h-[100px]"
                  placeholder="Describe your video scene..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Character (optional)</label>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  value={selectedCharacter || ""}
                  onChange={(e) =>
                    setSelectedCharacter(e.target.value ? Number(e.target.value) : null)
                  }
                >
                  <option value="">No character</option>
                  {characters?.map((char: any) => (
                    <option key={char.id} value={char.id}>
                      {char.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Aspect Ratio</label>
                <div className="grid grid-cols-4 gap-2">
                  {["9:16", "1:1", "16:9", "4:5"].map((ratio) => (
                    <button
                      key={ratio}
                      className={`px-3 py-2 border rounded-md text-sm ${
                        aspectRatio === ratio
                          ? "border-primary bg-primary/10"
                          : "border-input"
                      }`}
                      onClick={() => setAspectRatio(ratio)}
                    >
                      {ratio}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Quality</label>
                <div className="flex gap-2">
                  <button
                    className={`flex-1 px-3 py-2 border rounded-md text-sm ${
                      quality === "low"
                        ? "border-primary bg-primary/10"
                        : "border-input"
                    }`}
                    onClick={() => setQuality("low")}
                  >
                    Preview
                  </button>
                  <button
                    className={`flex-1 px-3 py-2 border rounded-md text-sm ${
                      quality === "high"
                        ? "border-primary bg-primary/10"
                        : "border-input"
                    }`}
                    onClick={() => setQuality("high")}
                  >
                    4K Final
                  </button>
                </div>
              </div>

              <Button
                className="w-full"
                onClick={handleGenerate}
                disabled={!prompt || generateMutation.isPending}
              >
                <Play className="w-4 h-4 mr-2" />
                {generateMutation.isPending ? "Generating..." : "Generate Video"}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Generation History</CardTitle>
              <CardDescription>Your recent video generations</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <p className="text-center text-muted-foreground py-8">Loading...</p>
              ) : !generations || generations.length === 0 ? (
                <div className="text-center py-8">
                  <Video className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">No generations yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {generations.map((gen: any) => (
                    <div
                      key={gen.id}
                      className="border rounded-lg p-4 hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {getStatusIcon(gen.status)}
                            <span className="font-medium capitalize">{gen.status}</span>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                            {gen.prompt}
                          </p>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground">
                            <span>{gen.aspect_ratio}</span>
                            <span>•</span>
                            <span>{gen.quality}</span>
                            <span>•</span>
                            <span>{gen.generation_type.replace(/_/g, " ")}</span>
                          </div>
                        </div>
                        {gen.output_video_path && (
                          <Button variant="outline" size="sm">
                            View
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
