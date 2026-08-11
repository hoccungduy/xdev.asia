import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

/**
 * Đọc kích thước thật của một ảnh trong `public/` bằng cách phân tích header.
 *
 * Vì sao cần: `buildArticleMetadata` từng khai cứng `og:image:width 1200 / height 630` cho MỌI bài,
 * trong khi ảnh thật trên site có nhiều cỡ — 138 ảnh 1920×1080, 45 ảnh 1600×900, 9 ảnh 960×720 (4:3),
 * và vài cỡ lẻ. Khai sai số làm Facebook dựng khung xem trước lệch tỉ lệ.
 *
 * Không thêm dependency: `sharp` chỉ có gián tiếp qua Next nên không đáng dựa vào.
 *
 * Trả `null` khi không đo được (ảnh ngoài site, SVG, hoặc FILE KHÔNG TỒN TẠI). Nơi gọi phải BỎ
 * width/height khi nhận `null` — khai số đoán còn tệ hơn không khai.
 */
export type ImageSize = { width: number; height: number };

function parsePng(b: Buffer): ImageSize | null {
  // 8 byte signature, rồi chunk IHDR: length(4) + "IHDR"(4) + width(4) + height(4)
  if (b.length < 24) return null;
  if (b.readUInt32BE(0) !== 0x89504e47) return null;
  if (b.toString("ascii", 12, 16) !== "IHDR") return null;
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) };
}

function parseJpeg(b: Buffer): ImageSize | null {
  if (b.length < 4 || b.readUInt16BE(0) !== 0xffd8) return null;
  let i = 2;
  while (i + 9 < b.length) {
    if (b[i] !== 0xff) { i += 1; continue; }
    const marker = b[i + 1];
    // SOF0..SOF15 trừ DHT(c4), JPG(c8), DAC(cc) — chỉ các marker này mang kích thước.
    if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
      return { height: b.readUInt16BE(i + 5), width: b.readUInt16BE(i + 7) };
    }
    if (marker === 0xd8 || marker === 0xd9 || (marker >= 0xd0 && marker <= 0xd7)) { i += 2; continue; }
    const len = b.readUInt16BE(i + 2);
    if (len < 2) return null;
    i += 2 + len;
  }
  return null;
}

function parseWebp(b: Buffer): ImageSize | null {
  if (b.length < 30) return null;
  if (b.toString("ascii", 0, 4) !== "RIFF" || b.toString("ascii", 8, 12) !== "WEBP") return null;
  const chunk = b.toString("ascii", 12, 16);
  if (chunk === "VP8 ") {
    // Frame header: 3 byte tag + 3 byte sync, rồi width/height 14 bit little-endian.
    return { width: b.readUInt16LE(26) & 0x3fff, height: b.readUInt16LE(28) & 0x3fff };
  }
  if (chunk === "VP8X") {
    // Canvas size trừ 1, mỗi chiều 24 bit little-endian.
    const w = b[24] | (b[25] << 8) | (b[26] << 16);
    const h = b[27] | (b[28] << 8) | (b[29] << 16);
    return { width: w + 1, height: h + 1 };
  }
  return null; // VP8L (lossless) — chưa cần, site không dùng.
}

/** Đường dẫn công khai (`/images/...`) → đường dẫn file trong `public/`. */
function toPublicPath(url: string): string | null {
  if (!url.startsWith("/")) return null;
  const clean = url.split("?")[0].split("#")[0];
  return path.join(process.cwd(), "public", clean);
}

const cache = new Map<string, ImageSize | null>();

export function getLocalImageSize(url: string): ImageSize | null {
  if (cache.has(url)) return cache.get(url) ?? null;

  let size: ImageSize | null = null;
  const file = toPublicPath(url);

  if (file && existsSync(file)) {
    const ext = path.extname(file).toLowerCase();
    try {
      // Đọc 64 KB đầu là đủ cho mọi header ở đây; JPEG có thể cần quét xa hơn nên đọc cả file
      // khi là JPEG. Ảnh trên site cỡ ~1 MB nên không đáng lo về bộ nhớ ở bước build.
      const buf = readFileSync(file);
      if (ext === ".png") size = parsePng(buf);
      else if (ext === ".jpg" || ext === ".jpeg") size = parseJpeg(buf);
      else if (ext === ".webp") size = parseWebp(buf);
      // .svg không có kích thước pixel nội tại → để null.
    } catch {
      size = null;
    }
  } else if (file) {
    // File được khai trong frontmatter nhưng KHÔNG tồn tại → og:image sẽ 404 và Facebook không
    // dựng được ảnh xem trước. Đây đúng là lỗi đã xảy ra với 7 bài microservices, và nó im lặng.
    // In ra lúc build để lần sau thấy ngay.
    console.warn(`[seo] featured_image không tồn tại trong public/: ${url}`);
  }

  cache.set(url, size);
  return size;
}
