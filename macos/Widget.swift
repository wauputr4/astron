import SwiftUI
import WidgetKit
import Darwin

struct Reflection: Codable {
    let date: String
    let topic: String
    let question: String
    let action: String
    let lesson_label: String
    static var generic: Reflection {
        Reflection(date: "", topic: "Ruang untuk refleksi", question: "Apa yang ingin kamu beri perhatian hari ini?", action: "Luangkan dua menit untuk mencatat satu pengalaman.", lesson_label: "Belum ada pelajaran disetujui untuk dirujuk.")
    }
}
struct DataFile: Codable { let entries: [Reflection] }
struct Entry: TimelineEntry { let date: Date; let value: Reflection }
struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> Entry { Entry(date: Date(), value: .generic) }
    func getSnapshot(in context: Context, completion: @escaping (Entry) -> Void) { completion(readEntry()) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
        completion(Timeline(entries: [readEntry()], policy: .after(Date().addingTimeInterval(3600))))
    }
    func readEntry() -> Entry {
        // A sandboxed extension's homeDirectory is its container, not the owner home.
        guard let owner = getpwuid(getuid()) else { return Entry(date: Date(), value: .generic) }
        let home = URL(fileURLWithPath: String(cString: owner.pointee.pw_dir), isDirectory: true)
        let url = home.appendingPathComponent("Library/Application Support/astron/widget-reflections.json")
        var value = Reflection.generic
        if let values = try? url.resourceValues(forKeys: [.isSymbolicLinkKey]), values.isSymbolicLink != true,
           let data = try? Data(contentsOf: url),
           let cached = try? JSONDecoder().decode(DataFile.self, from: data).entries.first {
            // Treat cache as untrusted: desktop never renders arbitrary profile/journal strings.
            let question = cached.question == "Apa yang paling terasa hari ini, sebelum membaca tafsir?" ? cached.question : value.question
            let allowedActions = ["Coba satu langkah kecil yang sudah kamu pilih.", "Pilih satu langkah kecil yang ada dalam kendalimu."]
            let action = allowedActions.contains(cached.action) ? cached.action : value.action
            let lesson = cached.lesson_label == "Ada pelajaran disetujui · tinjau secara privat di Astron." ? cached.lesson_label : value.lesson_label
            value = Reflection(date: "", topic: value.topic, question: question, action: action, lesson_label: lesson)
        }
        return Entry(date: Date(), value: value)
    }
}
struct ReflectionView: View {
    let entry: Entry
    @Environment(\.widgetFamily) private var family
    var body: some View {
        Link(destination: URL(string: "astron://capture")!) {
            VStack(alignment: .leading, spacing: 10) {
                Label("ASTRON", systemImage: "sparkles")
                    .font(.system(size: 10, weight: .semibold)).tracking(1.5)
                Spacer(minLength: 0)
                Text(entry.value.question)
                    .font(.system(size: family == .systemSmall ? 16 : 18, weight: .medium, design: .serif))
                    .fixedSize(horizontal: false, vertical: true)
                    .lineLimit(3)
                if family == .systemMedium {
                    Text(entry.value.action).font(.system(size: 11)).lineLimit(2)
                    Text(entry.value.lesson_label).font(.system(size: 10)).foregroundStyle(.white.opacity(0.75)).lineLimit(2)
                }
                Spacer(minLength: 0)
                HStack {
                    Text("Catat pengalaman")
                    Spacer()
                    Image(systemName: "arrow.up.right")
                }.font(.system(size: 11, weight: .medium))
            }.frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        }
        .containerBackground(for: .widget) { Color(red: 0.10, green: 0.09, blue: 0.19) }
        .foregroundStyle(.white)
    }
}
struct AstronWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "com.wauputr4.astron.daily", provider: Provider()) { ReflectionView(entry: $0) }
            .configurationDisplayName("Astron — Refleksi Hari Ini")
            .description("Satu pertanyaan, satu langkah kecil, dan rujukan pelajaran yang disetujui. Nama dan rincian relasi selalu disembunyikan.")
            .supportedFamilies([.systemSmall, .systemMedium])
    }
}

@main struct AstronWidgets: WidgetBundle {
    var body: some Widget { AstronWidget(); SkyCalendarWidget() }
}
