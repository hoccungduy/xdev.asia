import BookmarkButton from "@/components/BookmarkButton";
import ContentLanguageSwitcher from "@/components/ContentLanguageSwitcher";
import ContentRenderer from "@/components/ContentRenderer";
import DomainSeriesLayout from "@/components/DomainSeriesLayout";
import GiscusComments from "@/components/GiscusComments";
import { IconChevronRight, IconStar } from "@/components/Icons";
import { LessonCheckbox, SeriesProgressCard } from "@/components/SeriesProgress";
import ShareButtons from "@/components/ShareButtons";
import TableOfContents from "@/components/TableOfContents";
import { getAuthorById, getSeries, getSeriesCategories, getSeriesLanguageLinks, getSeriesSlugsWithCategory } from "@/lib/data";
import { getValidImageUrl } from "@/utils/image";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getLocalImageSize } from "@/lib/image-size";

export const dynamicParams = false;

export function generateStaticParams() {
    return getSeriesSlugsWithCategory().map(({ category, slug }) => ({ category, slug }));
}

const SITE_URL = "https://xdev.asia";

export async function generateMetadata({ params }: { params: Promise<{ category: string; slug: string }> }): Promise<Metadata> {
    const { category, slug } = await params;
    const series = getSeries(slug);
    if (!series) return {};

    const canonicalUrl = `${SITE_URL}/series/${category}/${slug}/`;
    const rawImageUrl = getValidImageUrl(series.featured_image ?? null, slug);
    const imageUrl = rawImageUrl.startsWith("http") ? rawImageUrl : `${SITE_URL}${rawImageUrl}`;

    return {
        title: series.title,
        description: series.description || series.title,
        alternates: { canonical: canonicalUrl },
        openGraph: {
            title: series.title,
            description: series.description || series.title,
            url: canonicalUrl,
            siteName: "xDev Asia",
            locale: "vi_VN",
            type: "article",
            // Cùng lý do như trong lib/seo.ts: đo từ file thật, thiếu thì bỏ width/height.
            images: [{ url: imageUrl, ...(getLocalImageSize(series.featured_image ?? "") ?? {}), alt: series.title }],
        },
        twitter: {
            card: "summary_large_image",
            title: series.title,
            description: series.description || series.title,
            images: [imageUrl],
        },
    };
}

export default async function SeriesDetailPage({ params }: { params: Promise<{ category: string; slug: string }> }) {
    const { category, slug } = await params;
    const series = getSeries(slug);
    if (!series) notFound();

    // Validate category matches
    const seriesCategory = series.category?.slug || "uncategorized";
    if (seriesCategory !== category) notFound();

    const categories = getSeriesCategories();
    const cat = categories.find((c) => c.slug === category);
    const fullAuthor = getAuthorById(series.author?.id);

    // GitBook-style layout for domain category
    if (category === "domain") {
        return (
            <DomainSeriesLayout
                series={series}
                category={category}
                categoryName={cat?.name || category}
                fullAuthor={fullAuthor || null}
                siteUrl={SITE_URL}
            />
        );
    }

    const levelLabels: Record<string, string> = {
        beginner: "Cơ bản",
        intermediate: "Trung cấp",
        advanced: "Nâng cao",
    };

    const totalLessons = series.sections.reduce((sum, s) => sum + s.lessons.length, 0);
    const displayLessons = totalLessons || series.lesson_count || 0;

    const stats: { value: string; label: string }[] = [];
    if (displayLessons > 0) stats.push({ value: String(displayLessons), label: "Bài học" });
    if (series.duration_hours) stats.push({ value: `${series.duration_hours}h`, label: "Thời lượng" });
    if (series.average_rating > 0) stats.push({ value: Number(series.average_rating).toFixed(1), label: `Đánh giá (${series.review_count})` });
    if (series.view_count > 0) stats.push({ value: series.view_count.toLocaleString("vi-VN"), label: "Lượt xem" });

    const firstLesson = series.sections[0]?.lessons[0];
    const primaryHref = firstLesson
        ? `/lessons/${series.slug}/${firstLesson.slug}/`
        : series.content
            ? "#noi-dung"
            : null;
    const primaryLabel = firstLesson ? "Học ngay" : "Đọc nội dung";

    return (
        <div>
            {/* Series Hero */}
            <div className="hero-gradient">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
                    {/* Breadcrumb */}
                    <nav className="flex items-center gap-2 text-[12px] mb-8" style={{ color: "var(--n-muted)" }}>
                        <Link href="/" className="hover:text-[var(--n-text)] transition-colors">Trang chủ</Link>
                        <IconChevronRight size={12} />
                        <Link href="/series/" className="hover:text-[var(--n-text)] transition-colors">Series</Link>
                        <IconChevronRight size={12} />
                        <Link href={`/series/${category}/`} className="hover:text-[var(--n-text)] transition-colors">
                            {cat?.name || category}
                        </Link>
                        <IconChevronRight size={12} />
                        <span className="truncate max-w-50" style={{ color: "var(--n-text)" }}>{series.title}</span>
                    </nav>

                    <div className="grid grid-cols-1 lg:grid-cols-[1.25fr_.75fr] gap-14 items-start">
                        {/* Left: Series Info */}
                        <div>
                            <div className="flex flex-wrap items-center gap-2 mb-5">
                                <span className="tag-accent uppercase tracking-wide">
                                    {levelLabels[series.level] || series.level}
                                </span>
                                <span className="tag-neutral">
                                    {series.is_free ? "Miễn phí" : `${Number(series.price).toLocaleString("vi-VN")}đ`}
                                </span>
                            </div>

                            <h1 className="text-[30px] md:text-[42px] font-medium leading-[1.15] mb-4" style={{ color: "var(--n-text)" }}>
                                {series.title}
                            </h1>

                            {series.description && (
                                <p className="text-[17px] leading-relaxed mb-6 max-w-2xl" style={{ color: "var(--n-muted)" }}>
                                    {series.description}
                                </p>
                            )}

                            {/* Stats row */}
                            {stats.length > 0 && (
                                <div className="flex flex-wrap gap-x-8 gap-y-4 mb-8 pt-5" style={{ borderTop: "1px solid var(--n-divider)" }}>
                                    {stats.map((stat) => (
                                        <div key={stat.label}>
                                            <div className="tabular-nums text-[20px] font-medium" style={{ color: "var(--n-text)" }}>
                                                {stat.value}
                                            </div>
                                            <div className="text-[12px] mt-0.5" style={{ color: "var(--n-muted)" }}>
                                                {stat.label}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* CTA buttons */}
                            <div className="flex flex-wrap items-center gap-3 mb-6">
                                {primaryHref && (
                                    <Link href={primaryHref} className="btn-primary">
                                        {primaryLabel}
                                    </Link>
                                )}
                                {totalLessons > 0 && (
                                    <Link href="#curriculum" className="btn-secondary">
                                        Xem chương trình
                                    </Link>
                                )}
                            </div>

                            {series.tags.length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                    {series.tags.map((tag) => (
                                        <Link key={tag.slug} href={`/tags/${tag.slug}/`} className="tag-pill">
                                            {tag.name}
                                        </Link>
                                    ))}
                                </div>
                            )}

                            <ContentLanguageSwitcher
                                links={getSeriesLanguageLinks(series)}
                                currentLocale="vi"
                                className="mt-6"
                            />
                        </div>

                        {/* Right: Progress card */}
                        {totalLessons > 0 && (
                            <SeriesProgressCard seriesSlug={series.slug} totalLessons={totalLessons} sections={series.sections} />
                        )}
                    </div>
                </div>
            </div>

            {/* Featured image banner */}
            {series.featured_image && (
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 lg:pt-14">
                    <div className="rounded-lg overflow-hidden" style={{ boxShadow: "0 0 0 1px var(--n-divider)" }}>
                        <Image
                            src={getValidImageUrl(series.featured_image, series.slug)}
                            alt={series.title}
                            width={1200}
                            height={675}
                            style={{ height: "auto" }}
                            className="w-full h-auto aspect-video object-cover"
                            priority
                        />
                    </div>
                </div>
            )}

            {/* Content Area */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 lg:py-18">
                <div className={`grid grid-cols-1 gap-14 ${series.content ? "lg:grid-cols-[minmax(0,800px)_260px]" : ""}`}>
                    {/* Main Content */}
                    <article className="min-w-0">
                        {/* Curriculum Section */}
                        {series.sections.length > 0 && (
                            <section id="curriculum" className="mb-16">
                                <h2 className="text-[22px] font-medium mb-1" style={{ color: "var(--n-text)" }}>
                                    Nội dung series
                                </h2>
                                <p className="text-[13px] mb-8" style={{ color: "var(--n-muted)" }}>
                                    {series.sections.length} phần · {totalLessons} bài học
                                </p>
                                <div className="space-y-8">
                                    {series.sections.map((section, sIdx) => (
                                        <div key={section.id}>
                                            <div className="flex items-center justify-between gap-3 pb-3" style={{ borderBottom: "1px solid var(--n-divider)" }}>
                                                <h3 className="flex items-center gap-2 text-[17px] font-medium" style={{ color: "var(--n-text)" }}>
                                                    <span className="tabular-nums text-[12px]" style={{ color: "var(--n-accent)" }}>
                                                        {String(sIdx + 1).padStart(2, "0")}
                                                    </span>
                                                    {section.title}
                                                </h3>
                                                <span className="text-[11.5px] shrink-0" style={{ color: "var(--n-muted)" }}>
                                                    {section.lessons.length} bài
                                                </span>
                                            </div>
                                            <ul>
                                                {section.lessons.map((lesson) => (
                                                    <li
                                                        key={lesson.id}
                                                        className="flex items-center gap-3"
                                                        style={{ padding: "12px 0", borderBottom: "1px solid var(--n-hair)" }}
                                                    >
                                                        <LessonCheckbox seriesSlug={series.slug} lessonSlug={lesson.slug} />
                                                        <Link
                                                            href={`/lessons/${series.slug}/${lesson.slug}/`}
                                                            className="flex-1 text-[14.5px] transition-colors hover:text-[var(--n-accent)]"
                                                            style={{ color: "var(--n-text)" }}
                                                        >
                                                            {lesson.title}
                                                        </Link>
                                                        {lesson.duration_minutes && (
                                                            <span className="tabular-nums text-[11.5px] shrink-0" style={{ color: "var(--n-muted)" }}>
                                                                {lesson.duration_minutes} phút
                                                            </span>
                                                        )}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Series Content (HTML) */}
                        {series.content && (
                            <div id="noi-dung">
                                <ContentRenderer html={series.content} />
                            </div>
                        )}

                        {/* Share & Bookmark */}
                        <div className="mt-10 pt-8 flex flex-wrap items-center justify-between gap-4" style={{ borderTop: "1px solid var(--n-hair)" }}>
                            <ShareButtons title={series.title} url={`${SITE_URL}/series/${category}/${slug}/`} />
                            <BookmarkButton
                                slug={`series-${series.slug}`}
                                title={series.title}
                                excerpt={series.description}
                                featured_image={series.featured_image}
                                category={cat?.name || null}
                            />
                        </div>

                        {/* Author Profile Card */}
                        {fullAuthor && (
                            <Link href="/gioi-thieu/" className="block mt-16 p-8 glass-card">
                                <div className="flex flex-col sm:flex-row items-start gap-5">
                                    {fullAuthor.avatar ? (
                                        <Image
                                            src={getValidImageUrl(fullAuthor.avatar, fullAuthor.name)}
                                            alt={fullAuthor.name}
                                            width={72}
                                            height={72}
                                            style={{ height: "auto" }}
                                            className="rounded-lg object-cover shrink-0"
                                        />
                                    ) : (
                                        <div
                                            className="w-18 h-18 rounded-lg flex items-center justify-center font-medium text-2xl shrink-0"
                                            style={{ background: "var(--n-accent-soft)", color: "var(--n-accent-ink)" }}
                                        >
                                            {fullAuthor.name.charAt(0)}
                                        </div>
                                    )}
                                    <div className="min-w-0">
                                        <div className="section-label mb-1">Tác giả</div>
                                        <h3 className="text-[19px] font-medium mb-2" style={{ color: "var(--n-text)" }}>{fullAuthor.name}</h3>
                                        {fullAuthor.bio && (
                                            <p className="text-[14px] leading-relaxed" style={{ color: "var(--n-muted)" }}>{fullAuthor.bio}</p>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        )}

                        {/* Reviews */}
                        {series.reviews && series.reviews.length > 0 && (
                            <section className="mt-12 pt-10" style={{ borderTop: "1px solid var(--n-hair)" }}>
                                <h2 className="flex items-center gap-3 text-[22px] font-medium mb-8" style={{ color: "var(--n-text)" }}>
                                    <IconStar size={20} className="fill-current text-[var(--n-accent)]" />
                                    Đánh giá ({series.reviews.length})
                                </h2>

                                {/* Rating summary */}
                                <div className="flex items-center gap-6 mb-10 p-6 card">
                                    <div className="text-center">
                                        <div className="text-[40px] font-medium tabular-nums" style={{ color: "var(--n-text)" }}>
                                            {Number(series.average_rating).toFixed(1)}
                                        </div>
                                        <div className="flex items-center gap-0.5 mt-2 justify-center">
                                            {[1, 2, 3, 4, 5].map((star) => (
                                                <IconStar
                                                    key={star}
                                                    size={16}
                                                    className={`fill-current ${star <= Math.round(Number(series.average_rating)) ? "text-[var(--n-accent)]" : "text-[var(--n-hair)]"}`}
                                                />
                                            ))}
                                        </div>
                                        <div className="text-[13px] mt-1" style={{ color: "var(--n-muted)" }}>{series.review_count} đánh giá</div>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    {series.reviews.map((review) => (
                                        <div key={review.id} className="p-5 glass-card">
                                            <div className="flex items-center gap-3 mb-3">
                                                <div
                                                    className="w-9 h-9 rounded-full flex items-center justify-center text-[12px] font-medium"
                                                    style={{ background: "var(--n-accent-soft)", color: "var(--n-accent-ink)" }}
                                                >
                                                    {review.user.name.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="text-[14px] font-medium" style={{ color: "var(--n-text)" }}>{review.user.name}</div>
                                                    <div className="flex items-center gap-0.5">
                                                        {[1, 2, 3, 4, 5].map((star) => (
                                                            <IconStar
                                                                key={star}
                                                                size={12}
                                                                className={`fill-current ${star <= review.rating ? "text-[var(--n-accent)]" : "text-[var(--n-hair)]"}`}
                                                            />
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                            {review.comment && (
                                                <p className="text-[14px] leading-relaxed" style={{ color: "var(--n-muted)" }}>{review.comment}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Comments — Giscus (GitHub Discussions) */}
                        <GiscusComments term={`/series/${series.category?.slug || "uncategorized"}/${series.slug}/`} />
                    </article>

                    {/* Sidebar — Table of Contents */}
                    {series.content && (
                        <aside className="hidden lg:block">
                            <div className="sticky top-24">
                                <TableOfContents html={series.content} />
                            </div>
                        </aside>
                    )}
                </div>
            </div>
        </div>
    );
}
