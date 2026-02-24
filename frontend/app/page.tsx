'use client';

import HeaderNav from '@/components/HeaderNav';
import { useState } from 'react';
import {
  Box,
  Button,
  Input,
  Text,
  VStack,
  List,
  ListItem,
} from '@chakra-ui/react';


const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:80';

interface Citation {
  source: string;
  text: string;
}

interface QueryOutput {
  query: string;
  response: string;
  citations: Citation[];
}

export default function Page() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<QueryOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      fetch("http://localhost/query?q=test")
      .then(r => r.json())
      .then(console.log)
      .catch(console.error);
      const res = await fetch(
        `${API_BASE}/query?q=${encodeURIComponent(input.trim())}`
      );
      if (!res.ok) throw new Error(res.statusText);
      const data: QueryOutput = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <HeaderNav signOut={() => {}} />
      <Box maxWidth="720px" mx="auto">
        <Text fontSize="lg">
          Ask a question about Westeros laws
        </Text>
        <form onSubmit={handleSubmit}>
          <VStack align="stretch">
            <Input
              placeholder="e.g. What happens if I steal?"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <Button type="submit" colorScheme="blue" isLoading={loading}>
              Query
            </Button>
          </VStack>
        </form>

        {error && (
          <Text color="red">
            {error}
          </Text>
        )}

        {result && (
          <Box borderColor="gray.200">
            <Text fontWeight="semibold">
              Your question
            </Text >
            <Text>{result.query}</Text>
            <Text>
              Answer
            </Text>
            <Text fontWeight="semibold">
              {result.response}
            </Text>
            {result.citations.length > 0 && (
              <>
                <Text fontWeight="semibold">
                  Citations
                </Text>
                <List>
                  {result.citations.map((c, i) => (
                    <ListItem key={i}>
                      <Text as="span" fontWeight="medium" color="gray.600">
                        {c.source}:
                      </Text>{' '}
                      {c.text.slice(0, 500)}
                      {c.text.length > 200 ? '…' : ''}
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </Box>
        )}
      </Box>
    </>
  );
}