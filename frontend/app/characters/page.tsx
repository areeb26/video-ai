"use client";

import { useQuery } from "@tanstack/react-query";
import { characterApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, User } from "lucide-react";
import Link from "next/link";

export default function CharactersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["characters"],
    queryFn: async () => {
      const response = await characterApi.getAll();
      return response.data;
    },
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Characters</h1>
          <p className="text-muted-foreground">
            Create and manage character profiles with face embeddings and style locks
          </p>
        </div>
        <Link href="/characters/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Character
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading characters...</p>
        </div>
      ) : !data || data.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <User className="w-16 h-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No characters yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first character to get started with consistent video generation
            </p>
            <Link href="/characters/new">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Character
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.map((character: any) => (
            <Link key={character.id} href={`/characters/${character.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="w-5 h-5" />
                    {character.name}
                  </CardTitle>
                  <CardDescription>
                    {character.age && `Age: ${character.age}`}
                    {character.stable_id && (
                      <span className="block text-xs mt-1">ID: {character.stable_id}</span>
                    )}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    {character.hair_color && (
                      <div>
                        <span className="text-muted-foreground">Hair:</span> {character.hair_color}
                      </div>
                    )}
                    {character.eye_color && (
                      <div>
                        <span className="text-muted-foreground">Eyes:</span> {character.eye_color}
                      </div>
                    )}
                    {character.face_references && (
                      <div>
                        <span className="text-muted-foreground">Face refs:</span>{" "}
                        {character.face_references.length}
                      </div>
                    )}
                    {character.outfits && (
                      <div>
                        <span className="text-muted-foreground">Outfits:</span> {character.outfits.length}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
