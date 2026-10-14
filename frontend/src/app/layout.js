import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata = {
  title: "RetailPulse AI - Customer Analytics & Product Recommender",
  description: "Minimalist executive dashboard and live product recommendation engine powered by RFM K-Means and FP-Growth association rules.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <main style={{ flex: 1, paddingBottom: '48px' }}>
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
