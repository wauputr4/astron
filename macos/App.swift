import SwiftUI
import WidgetKit
import AppKit
import Darwin

private func ownerHome() -> URL {
    guard let record = getpwuid(getuid()) else { return FileManager.default.homeDirectoryForCurrentUser }
    return URL(fileURLWithPath: String(cString: record.pointee.pw_dir), isDirectory: true)
}

@MainActor final class JournalModel: ObservableObject {
    struct Profile: Identifiable { let id: String; let label: String }
    @Published var profiles: [Profile] = []
    @Published var selection = ""
    @Published var journalRoot = ""
    @Published var savedSelection = ""
    @Published var savedRoot = ""
    var selectedProfileIsApplied: Bool { !selection.isEmpty && selection == savedSelection && journalRoot == savedRoot }
    @Published var experience = ""
    @Published var consent = false
    @Published var busy = false
    @Published var status = "Widget menyembunyikan nama dan rincian relasi."
    @Published var lesson = "Rujukan pelajaran disetujui hanya dibuka secara privat."
    @Published var approvedLessons: [String] = []
    @Published var showLessons = false
    @Published var showSky = false
    @Published var sky: SkyData? = SkyData.read()
    @Published var skyMonth = String(DateFormatter.localizedString(from: Date(), dateStyle: .short, timeStyle: .none))
    @Published var skyTimezone = "Asia/Jakarta"
    @Published var skyPersonal = false
    @Published var skySelected = ""

    func calculateSky() {
        call(["operation": "sky", "month": skyMonth, "timezone": skyTimezone,
              "personal": skyPersonal, "consent": skyPersonal]) { result in
            if let bytes = try? JSONSerialization.data(withJSONObject: result),
               let data = try? JSONDecoder().decode(SkyData.self, from: bytes) {
                self.sky = data
                self.skySelected = ""
                self.status = "Kalender dihitung lokal. Interpretasi simbolik, bukan kepastian."
                WidgetCenter.shared.reloadAllTimelines()
            }
        }
    }
    func clearSky() {
        call(["operation": "sky_clear"]) { _ in
            self.sky = nil
            self.skyPersonal = false
            self.status = "Cache kalender dihapus. Data jurnal tidak diubah."
            WidgetCenter.shared.reloadAllTimelines()
        }
    }

    func call(_ payload: [String: Any], completion: @escaping ([String: Any]) -> Void) {
        guard !busy else { return }
        busy = true
        let input = (try? JSONSerialization.data(withJSONObject: payload)) ?? Data()
        DispatchQueue.global(qos: .userInitiated).async {
            let process = Process()
            // Apple ships Python with CLT, already required to build this app.
            process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
            process.arguments = [Bundle.main.resourceURL!.appendingPathComponent("generate.py").path]
            let stdin = Pipe(); let stdout = Pipe(); let stderr = Pipe()
            process.standardInput = stdin; process.standardOutput = stdout; process.standardError = stderr
            var response: [String: Any] = [:]
            do {
                try process.run()
                stdin.fileHandleForWriting.write(input)
                try? stdin.fileHandleForWriting.close()
                let data = stdout.fileHandleForReading.readDataToEndOfFile()
                process.waitUntilExit()
                response = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any] ?? [:]
            } catch { }
            let result = response
            DispatchQueue.main.async {
                self.busy = false
                if let error = result["error"] as? String { self.status = error }
                else if result.isEmpty { self.status = "Bridge lokal tidak tersedia. Periksa Python Command Line Tools." }
                else { completion(result) }
            }
        }
    }
    func load() {
        call(["operation": "profiles"]) { result in
            self.profiles = (result["profiles"] as? [[String: String]] ?? []).compactMap {
                guard let id = $0["id"], let label = $0["label"] else { return nil }
                return Profile(id: id, label: label)
            }
            let selected = result["selected"] as? String ?? ""
            self.selection = self.profiles.contains(where: { $0.id == selected }) ? selected : ""
            self.journalRoot = result["journal_root"] as? String ?? ownerHome().appendingPathComponent("Library/Application Support/astron").path
            self.savedSelection = self.selection
            self.savedRoot = self.journalRoot
            self.status = result["notice"] as? String ?? "Hanya profil diri ditampilkan; nama dan rincian relasi disembunyikan."
        }
    }
    func select() {
        call(["operation": "select", "profile_id": selection, "journal_root": journalRoot, "consent": true]) { result in
            self.lesson = result["lesson_label"] as? String ?? self.lesson
            self.sky = SkyData.read()
            self.skyPersonal = false
            self.status = self.selection.isEmpty ? "Mode generik aktif. Tidak ada profil pribadi dipakai." : "Profil diri dipilih. Widget hanya menampilkan teks generik yang aman."
            WidgetCenter.shared.reloadAllTimelines()
            self.load()
        }
    }
    func refresh() {
        call(["operation": "refresh"]) { result in
            self.lesson = result["lesson_label"] as? String ?? self.lesson
            self.status = "Refleksi lokal diperbarui."
            WidgetCenter.shared.reloadAllTimelines()
        }
    }
    func learning() {
        guard selectedProfileIsApplied else { return }
        call(["operation": "learning"]) { result in
            self.approvedLessons = (result["lessons"] as? [[String: String]] ?? []).compactMap { $0["text"] }
            self.showLessons = true
        }
    }
    func save() {
        guard selectedProfileIsApplied else { return }
        call(["operation": "capture", "experience": experience, "consent": consent]) { _ in
            self.experience = ""; self.consent = false
            self.status = "Pengalaman tersimpan di jurnal profil diri. Bukan validasi ilmiah atau pelajaran otomatis."
            WidgetCenter.shared.reloadAllTimelines()
        }
    }
}

struct ReflectionCard: View {
    @ObservedObject var model: JournalModel
    @State private var expanded = false
    @State private var settings = false
    @FocusState private var captureFocused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Label("Astron", systemImage: "sparkles")
                    .font(.system(size: 19, weight: .semibold, design: .serif))
                Spacer()
                Button { settings.toggle(); expanded = true } label: { Image(systemName: "gearshape") }
                    .buttonStyle(.plain).help("Pengaturan")
                    .accessibilityLabel("Pengaturan")
            }
            Text("Apa yang terasa hari ini?")
                .font(.system(size: 22, weight: .medium, design: .serif))
            Text("Ambil dua menit untuk dirimu.")
                .font(.callout).foregroundStyle(.secondary)
            Button("Langit & Kamu", systemImage: "moon.stars") { model.showSky = true }
                .buttonStyle(.bordered)
            Button {
                expanded.toggle()
                if !expanded { settings = false }
            } label: {
                HStack {
                    Text(expanded ? "Ringkas" : "Buka refleksi")
                    Spacer()
                    Image(systemName: expanded ? "chevron.up" : "arrow.up.right")
                }.padding(.vertical, 4)
            }.buttonStyle(.borderedProminent)
            if expanded {
                Divider()
                if settings {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Jurnal privat").font(.headline)
                        Picker("Profil", selection: $model.selection) {
                            Text("Generik — tanpa profil").tag("")
                            ForEach(model.profiles) { Text($0.label).tag($0.id) }
                        }
                        TextField("Lokasi jurnal", text: $model.journalRoot)
                            .textFieldStyle(.roundedBorder)
                        HStack {
                            Button("Terapkan") { model.select() }
                            Button("Muat ulang") { model.load() }
                            Button("Perbarui widget") { model.refresh() }
                        }.controlSize(.small)
                        Text("Hanya profil diri. Nama dan isi jurnal tidak tampil di widget.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Divider()
                }
                if model.selectedProfileIsApplied {
                    TextEditor(text: $model.experience)
                        .font(.body).frame(height: 100)
                        .overlay(RoundedRectangle(cornerRadius: 6).stroke(.secondary.opacity(0.25)))
                        .focused($captureFocused).accessibilityLabel("Pengalaman pribadi")
                    Toggle("Simpan catatan ini ke jurnal lokal saya", isOn: $model.consent)
                        .font(.caption)
                    HStack {
                        Button("Simpan") { model.save() }
                            .buttonStyle(.borderedProminent)
                            .disabled(!model.consent || model.experience.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || model.experience.count > 10000)
                        Spacer()
                        Button("Pelajaran") { model.learning() }
                    }
                } else {
                    Text("Belum ada jurnal yang terhubung.").font(.headline)
                    Text("Kamu tetap bisa berefleksi. Hubungkan profil diri untuk menyimpan catatan.")
                        .font(.callout).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                    Button("Hubungkan jurnal") { settings = true }
                }
                Text(model.status).font(.caption).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true).fixedSize(horizontal: false, vertical: true)
                    .accessibilityIdentifier("status")
            }
            HStack(spacing: 4) {
                Image(systemName: "lock.fill")
                Text("Lokal · privat · refleksi simbolik")
                Spacer()
                if model.busy { ProgressView().controlSize(.mini) }
            }.font(.system(size: 10)).foregroundStyle(.secondary)
        }
        .padding(22).frame(width: expanded ? 390 : 300)
        .background(Color(nsColor: .windowBackgroundColor))
        .disabled(model.busy)
        .onAppear { model.load() }
        .sheet(isPresented: $model.showLessons) {
            VStack(alignment: .leading, spacing: 16) {
                Text("Pelajaran · privat").font(.headline)
                ScrollView {
                    VStack(alignment: .leading, spacing: 14) {
                        if model.approvedLessons.isEmpty { Text("Belum ada pelajaran aktif yang disetujui.") }
                        ForEach(Array(model.approvedLessons.enumerated()), id: \.offset) { _, lesson in
                            Text(lesson).textSelection(.enabled)
                        }
                    }
                }.frame(minHeight: 100, maxHeight: 240)
                Button("Tutup") { model.showLessons = false }
            }.padding(22).frame(width: 360)
        }
        .sheet(isPresented: $model.showSky) { SkyPanel(model: model) }
        .onOpenURL { url in
            guard url.scheme == "astron" else { return }
            if url.host == "sky" {
                model.skySelected = URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems?.first(where: { $0.name == "date" })?.value ?? ""
                model.showSky = true
                NSApplication.shared.activate(ignoringOtherApps: true)
                return
            }
            guard url.host == "capture" else { return }
            expanded = true
            NSApplication.shared.activate(ignoringOtherApps: true)
            NSApplication.shared.windows.first?.makeKeyAndOrderFront(nil)
            captureFocused = true
        }
    }
}

@main struct AstronApp: App {
    @StateObject private var model = JournalModel()
    var body: some Scene {
        WindowGroup("Astron") { ReflectionCard(model: model) }
            .windowResizability(.contentSize)
            .defaultPosition(.center)
    }
}

struct SkyPanel: View {
    @ObservedObject var model: JournalModel
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack { Label("Langit & Kamu", systemImage: "moon.stars").font(.title2); Spacer(); Button("Tutup") { model.showSky = false } }
            HStack {
                TextField("YYYY-MM", text: $model.skyMonth).frame(width: 90).accessibilityLabel("Bulan YYYY-MM")
                TextField("Zona waktu IANA", text: $model.skyTimezone).frame(width: 170)
                Button("Hitung / perbarui") { model.calculateSky() }
            }.textFieldStyle(.roundedBorder)
            Toggle("Izinkan kontak natal pribadi tampil di desktop", isOn: $model.skyPersonal)
                .disabled(!model.selectedProfileIsApplied)
            Text("Opsional: profil diri terpilih harus punya data lahir dan waktu diketahui. Nama dan data lahir tidak tampil; kontak natal tetap dapat terlihat oleh orang yang melihat desktop.")
                .font(.caption).foregroundStyle(.secondary)
            if let sky = model.sky {
                HStack(alignment: .top, spacing: 20) {
                    VStack(alignment: .leading, spacing: 10) {
                        SkyCalendarGrid(data: sky, selected: model.skySelected) { model.skySelected = $0 }.frame(width: 195)
                        Text("Titik oranye: ada peristiwa dalam cakupan kalkulator.").font(.caption).foregroundStyle(.secondary)
                        Text(sky.timezone).font(.caption)
                    }
                    ScrollView {
                        VStack(alignment: .leading, spacing: 14) {
                            let events = sky.events.filter { model.skySelected.isEmpty || $0.day == model.skySelected }
                            if events.isEmpty { Text("Tidak ada peristiwa terhitung pada tanggal ini; bukan berarti tidak ada kejadian dalam hidupmu.").font(.callout) }
                            ForEach(events) { event in
                                VStack(alignment: .leading, spacing: 5) {
                                    Text(event.day + " · " + event.clock).font(.caption).foregroundStyle(.secondary)
                                    Text(event.title).font(.headline)
                                    Text(event.theme).font(.subheadline).foregroundStyle(.orange)
                                    Text(event.interpretation).font(.callout)
                                    Text(event.personal).font(.caption)
                                    Text("UTC: " + event.utc).font(.system(size: 9)).foregroundStyle(.secondary)
                                }
                                Divider()
                            }
                        }.frame(maxWidth: .infinity, alignment: .leading)
                    }.frame(height: 300)
                }
                HStack {
                    Button("Semua tanggal") { model.skySelected = "" }
                    Button("Catat pengalaman") { model.showSky = false; NSWorkspace.shared.open(URL(string: "astron://capture")!) }
                    Spacer()
                    Button("Hapus cache / cabut tampilan personal") { model.clearSky() }
                }.controlSize(.small)
                Text(sky.notice).font(.caption).foregroundStyle(.secondary)
                Text("Diperbarui: " + sky.generated_utc).font(.system(size: 9)).foregroundStyle(.secondary)
            } else {
                Text("Belum ada kalender. Pilih bulan dan zona waktu, lalu hitung secara lokal. Tidak ada data contoh yang ditampilkan sebagai peristiwa nyata.")
                    .font(.callout).frame(height: 180)
            }
            HStack { if model.busy { ProgressView().controlSize(.small) }; Text(model.status).font(.caption).foregroundStyle(.secondary) }
        }.padding(22).frame(width: 650)
         .disabled(model.busy)
         .onAppear {
             let f = DateFormatter(); f.dateFormat = "yyyy-MM"; f.timeZone = TimeZone(identifier: model.skyTimezone)
             model.skyMonth = model.sky?.month ?? f.string(from: Date())
             model.skyTimezone = model.sky?.timezone ?? "Asia/Jakarta"
         }
    }
}
