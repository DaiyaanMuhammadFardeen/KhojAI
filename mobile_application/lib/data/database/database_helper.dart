import 'dart:async';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path_provider/path_provider.dart';
import '../models/conversation.dart';
import '../models/message.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  DatabaseHelper._internal();

  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    print('[DatabaseHelper] Initializing database...');
    _database = await _initDatabase();
    print('[DatabaseHelper] Database initialized');
    return _database!;
  }

  Future<Database> _initDatabase() async {
    try {
      final documentsDirectory = await getApplicationDocumentsDirectory();
      final path = join(documentsDirectory.path, 'khoj_ai.db');
      print('[DatabaseHelper] Database path: $path');

      return await openDatabase(path, version: 1, onCreate: _onCreate);
    } catch (e) {
      print('[DatabaseHelper] Error initializing database: $e');
      rethrow;
    }
  }

  Future<void> _onCreate(Database db, int version) async {
    try {
      print('[DatabaseHelper] Creating database tables...');
      await db.execute('''
        CREATE TABLE conversations(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT,
          createdAt INTEGER,
          updatedAt INTEGER
        )
      ''');

      await db.execute('''
        CREATE TABLE messages(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          conversationId INTEGER,
          role TEXT,
          content TEXT,
          timestamp INTEGER,
          FOREIGN KEY (conversationId) REFERENCES conversations(id) ON DELETE CASCADE
        )
      ''');
      print('[DatabaseHelper] Database tables created successfully');
    } catch (e) {
      print('[DatabaseHelper] Error creating tables: $e');
      rethrow;
    }
  }

  // Conversation CRUD operations
  Future<int> insertConversation(Conversation conversation) async {
    try {
      final db = await database;
      print('[DatabaseHelper] Inserting conversation: ${conversation.title}');
      final id = await db.insert('conversations', conversation.toMap());
      print('[DatabaseHelper] Conversation inserted with ID: $id');
      return id;
    } catch (e) {
      print('[DatabaseHelper] Error inserting conversation: $e');
      rethrow;
    }
  }

  Future<List<Conversation>> getAllConversations() async {
    try {
      final db = await database;
      print('[DatabaseHelper] Querying all conversations...');
      final List<Map<String, dynamic>> maps = await db.query(
        'conversations',
        orderBy: 'updatedAt DESC',
      );
      print('[DatabaseHelper] Found ${maps.length} conversations');

      return List.generate(maps.length, (i) {
        return Conversation.fromMap(maps[i]);
      });
    } catch (e) {
      print('[DatabaseHelper] Error querying conversations: $e');
      rethrow;
    }
  }

  Future<int> updateConversation(Conversation conversation) async {
    try {
      final db = await database;
      print('[DatabaseHelper] Updating conversation ID: ${conversation.id}');
      return await db.update(
        'conversations',
        conversation.toMap(),
        where: 'id = ?',
        whereArgs: [conversation.id],
      );
    } catch (e) {
      print('[DatabaseHelper] Error updating conversation: $e');
      rethrow;
    }
  }

  Future<int> deleteConversation(int id) async {
    try {
      final db = await database;
      print('[DatabaseHelper] Deleting conversation ID: $id');
      return await db.delete('conversations', where: 'id = ?', whereArgs: [id]);
    } catch (e) {
      print('[DatabaseHelper] Error deleting conversation: $e');
      rethrow;
    }
  }

  // Message CRUD operations
  Future<int> insertMessage(Message message) async {
    try {
      final db = await database;
      print(
        '[DatabaseHelper] Inserting message for conversation: ${message.conversationId}',
      );
      return await db.insert('messages', message.toMap());
    } catch (e) {
      print('[DatabaseHelper] Error inserting message: $e');
      rethrow;
    }
  }

  Future<List<Message>> getMessagesByConversation(int conversationId) async {
    try {
      final db = await database;
      print(
        '[DatabaseHelper] Querying messages for conversation: $conversationId',
      );
      final List<Map<String, dynamic>> maps = await db.query(
        'messages',
        where: 'conversationId = ?',
        whereArgs: [conversationId],
        orderBy: 'timestamp ASC',
      );
      print('[DatabaseHelper] Found ${maps.length} messages');

      return List.generate(maps.length, (i) {
        return Message.fromMap(maps[i]);
      });
    } catch (e) {
      print('[DatabaseHelper] Error querying messages: $e');
      rethrow;
    }
  }

  Future<int> updateMessage(Message message) async {
    try {
      final db = await database;
      print('[DatabaseHelper] Updating message ID: ${message.id}');
      return await db.update(
        'messages',
        message.toMap(),
        where: 'id = ?',
        whereArgs: [message.id],
      );
    } catch (e) {
      print('[DatabaseHelper] Error updating message: $e');
      rethrow;
    }
  }

  Future<int> deleteMessage(int id) async {
    try {
      final db = await database;
      print('[DatabaseHelper] Deleting message ID: $id');
      return await db.delete('messages', where: 'id = ?', whereArgs: [id]);
    } catch (e) {
      print('[DatabaseHelper] Error deleting message: $e');
      rethrow;
    }
  }
}
