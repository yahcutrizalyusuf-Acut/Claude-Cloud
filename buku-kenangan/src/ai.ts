import Anthropic from "@anthropic-ai/sdk";

// Fitur "Bantu tulis dengan AI": membuat draf ucapan singkat yang bisa
// diubah sendiri oleh penulis. Nonaktif kalau ANTHROPIC_API_KEY belum diisi.

export interface PermintaanDraf {
  untuk: string;
  acara: string;
  hubungan: string;
  nada: "resmi" | "santai" | "aceh";
  poin: string;
}

const PANDUAN_NADA: Record<PermintaanDraf["nada"], string> = {
  resmi: "Bahasa Indonesia yang sopan dan hangat, cocok untuk atasan atau guru.",
  santai: "Bahasa Indonesia santai dan akrab, seperti pesan ke teman dekat.",
  aceh: "Bahasa Aceh sehari-hari yang hangat. Kalau ragu dengan satu kata Aceh, pakai kata Indonesia.",
};

const SYSTEM = `Kamu membantu orang menulis ucapan untuk buku kenangan bersama.
Tulis satu ucapan pendek (3–5 kalimat) dari sudut pandang penulis, langsung ditujukan ke penerima.
Pakai detail yang diberikan penulis; jangan mengarang kejadian, nama, atau tanggal.
Kalau acaranya bernuansa religi (misalnya lepas haji), boleh sertakan doa singkat.
Balas hanya dengan teks ucapannya, tanpa judul, tanpa tanda kutip, tanpa penjelasan.`;

export function aiAktif(): boolean {
  return Boolean(process.env.ANTHROPIC_API_KEY);
}

let client: Anthropic | null = null;

export async function buatDraf(p: PermintaanDraf): Promise<string> {
  client ??= new Anthropic();

  const isi = [
    `Penerima: ${p.untuk}`,
    `Acara: ${p.acara}`,
    p.hubungan && `Hubungan penulis dengan penerima: ${p.hubungan}`,
    `Nada: ${PANDUAN_NADA[p.nada]}`,
    p.poin && `Hal yang ingin disampaikan penulis: ${p.poin}`,
  ]
    .filter(Boolean)
    .join("\n");

  const response = await client.beta.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 2000,
    output_config: { effort: "low" },
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    system: SYSTEM,
    messages: [{ role: "user", content: isi }],
  });

  if (response.stop_reason === "refusal") {
    throw new Error("Draf tidak bisa dibuat untuk isian ini");
  }

  return response.content
    .flatMap((block) => (block.type === "text" ? [block.text] : []))
    .join("")
    .trim();
}
