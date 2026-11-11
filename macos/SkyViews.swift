import SwiftUI
import WidgetKit
import Darwin

struct SkyEvent: Codable, Identifiable {
    let id: String
    let kind: String
    let utc: String
    let local_time: String
    let day: String
    let title: String
    let theme: String
    let interpretation: String
    let personal: String
    var clock: String { String(local_time.dropFirst(11).prefix(5)) }
}
struct SkyData: Codable {
    let month: String
    let timezone: String
    let days: Int
    let first_weekday: Int
    let events: [SkyEvent]
    let generated_utc: String
    let personal_enabled: Bool
    let notice: String
    static func read() -> SkyData? {
        guard let owner = getpwuid(getuid()) else { return nil }
        let home = URL(fileURLWithPath: String(cString: owner.pointee.pw_dir))
        let url = home.appendingPathComponent("Library/Application Support/astron/sky-calendar.json")
        guard let values = try? url.resourceValues(forKeys: [.isSymbolicLinkKey]), values.isSymbolicLink != true,
              let bytes = try? Data(contentsOf: url), bytes.count < 2_000_000,
              let value = try? JSONDecoder().decode(SkyData.self, from: bytes),
              (1...31).contains(value.days), (0...6).contains(value.first_weekday) else { return nil }
        return value
    }
    var today: String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone(identifier: timezone)
        return f.string(from: Date())
    }
    var isCurrentMonth: Bool { month == String(today.prefix(7)) }
    var next: SkyEvent? {
        let formatter = ISO8601DateFormatter()
        return events.first { (formatter.date(from: $0.utc) ?? .distantPast) >= Date() }
    }
}
struct SkyCalendarGrid: View {
    let data: SkyData
    var selected: String = ""
    var widget: Bool = false
    var choose: (String) -> Void = { _ in }
    private let columns = Array(repeating: GridItem(.flexible(), spacing: 2), count: 7)
    var body: some View {
        VStack(spacing: widget ? 2 : 5) {
            Text(data.month).font(.system(size: widget ? 11 : 13, weight: .semibold, design: .rounded))
            LazyVGrid(columns: columns, spacing: widget ? 1 : 4) {
                ForEach(Array(["S", "S", "R", "K", "J", "S", "M"].enumerated()), id: \.offset) { _, label in
                    Text(label).font(.system(size: 8)).foregroundStyle(.secondary)
                }
                ForEach(0..<(data.first_weekday + data.days), id: \.self) { cell in
                    if cell < data.first_weekday { Color.clear.frame(height: widget ? 12 : 17) }
                    else {
                        let day = cell - data.first_weekday + 1
                        let key = data.month + String(format: "-%02d", day)
                        let marked = data.events.contains { $0.day == key }
                        if widget {
                            Link(destination: URL(string: "astron://sky?date=" + key)!) { dayCell(day, marked, key) }
                        } else {
                            Button { choose(key) } label: { dayCell(day, marked, key) }.buttonStyle(.plain)
                        }
                    }
                }
            }
        }
    }
    func dayCell(_ day: Int, _ marked: Bool, _ key: String) -> some View {
        VStack(spacing: 1) {
            Text(String(day)).font(.system(size: 10, weight: key == data.today ? .bold : .regular))
            Circle().fill(marked ? Color.orange : Color.clear).frame(width: 3, height: 3)
        }.frame(maxWidth: .infinity).frame(height: widget ? 12 : 17)
         .background(RoundedRectangle(cornerRadius: 4).fill(key == selected || key == data.today ? Color.orange.opacity(0.22) : Color.clear))
    }
}
struct SkyWidgetEntry: TimelineEntry { let date: Date; let sky: SkyData? }
struct SkyWidgetProvider: TimelineProvider {
    func placeholder(in context: Context) -> SkyWidgetEntry { SkyWidgetEntry(date: Date(), sky: nil) }
    func getSnapshot(in context: Context, completion: @escaping (SkyWidgetEntry) -> Void) { completion(SkyWidgetEntry(date: Date(), sky: SkyData.read())) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<SkyWidgetEntry>) -> Void) {
        completion(Timeline(entries: [SkyWidgetEntry(date: Date(), sky: SkyData.read())], policy: .after(Date().addingTimeInterval(1800))))
    }
}
struct SkyWidgetView: View {
    let entry: SkyWidgetEntry
    @Environment(\.widgetFamily) private var family
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Langit & Kamu", systemImage: "moon.stars").font(.system(size: 12, weight: .semibold))
            if let sky = entry.sky, sky.isCurrentMonth {
                HStack(alignment: .top, spacing: 14) {
                    SkyCalendarGrid(data: sky, widget: true).frame(width: family == .systemSmall ? 120 : 136)
                    if family != .systemSmall {
                        VStack(alignment: .leading, spacing: 5) {
                            if let event = sky.next {
                                Text(event.day + " · " + event.clock).font(.system(size: 10)).foregroundStyle(.secondary)
                                Text(event.title).font(.system(size: 13, weight: .semibold)).lineLimit(2)
                                Text(event.interpretation).font(.system(size: 10)).lineLimit(family == .systemLarge ? 5 : 3)
                                if sky.personal_enabled { Text(event.personal).font(.system(size: 9)).foregroundStyle(.orange).lineLimit(2) }
                            } else { Text("Tidak ada peristiwa berikutnya dalam cakupan bulan ini.").font(.caption) }
                        }
                    }
                }
                if family == .systemLarge {
                    Divider()
                    ForEach(Array(sky.events.filter { $0.day >= sky.today }.prefix(3))) { event in
                        Link(destination: URL(string: "astron://sky?date=" + event.day)!) {
                            HStack { Text(String(event.day.suffix(5))); Text(event.title).lineLimit(1); Spacer(); Text(event.clock) }.font(.system(size: 11))
                        }
                    }
                }
                if family != .systemSmall { Text("Simbolik · snapshot natal, bukan kepastian · " + sky.timezone).font(.system(size: 8)).foregroundStyle(.secondary) }
            } else {
                Link(destination: URL(string: "astron://sky")!) {
                    Text("Buka Astron untuk menghitung kalender bulan ini.").font(.caption)
                }
            }
        }.frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .containerBackground(for: .widget) { Color(red: 0.08, green: 0.10, blue: 0.17) }
        .foregroundStyle(.white)
        .widgetURL(URL(string: "astron://sky"))
    }
}
struct SkyCalendarWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "com.wauputr4.astron.sky", provider: SkyWidgetProvider()) { SkyWidgetView(entry: $0) }
            .configurationDisplayName("Astron — Langit & Kamu")
            .description("Kalender peristiwa langit, interpretasi simbolik, dan kontak natal opsional.")
            .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}
