export const metadata = {
  title: 'Language Listening Comprehension',
  description: 'Practice language listening comprehension with YouTube videos',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
